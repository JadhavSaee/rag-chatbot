import os
import re
from dotenv import load_dotenv
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()
model = SentenceTransformer("all-MiniLM-L6-v2")
col = chromadb.PersistentClient(path="db").get_collection("faq")
llm = Groq(api_key=os.getenv("GROQ_API_KEY"))

MAX_DISTANCE = 0.7
FALLBACK = "I don't have that information. Please call us at 0253-1234567."

SYSTEM = """You are a support assistant for Sunrise Health Clinic.
Answer ONLY using the provided context. Be concise and friendly.
Never invent prices, dates, or policies.
Never use gendered pronouns (he, she, him, her, his, hers) for any person. Always repeat the name, e.g. "Dr. Kulkarni sees patients on Tuesdays", or say "the doctor".
You are not a doctor. Never give medical advice or name medicines.
For health questions, suggest booking an appointment.
Never use outside knowledge. For any question unrelated to the clinic, reply exactly: "I don't have that information. Please call us at 0253-1234567."
If the answer is not in the context, reply exactly: "I don't have that information. Please call us at 0253-1234567." """


def answer(question, history=None):
    # follow-up handling: add the previous user question to short messages
    base = question
    if history and len(question.split()) <= 5:
        last_user = [m["content"] for m in history if m["role"] == "user"]
        if last_user:
            base = last_user[-1] + " " + question

    # search twice: with and without the clinic-name prefix, then merge
    hits = {}
    for text in ("Sunrise Health Clinic: " + base, base):
        res = col.query(query_embeddings=[model.encode(text).tolist()], n_results=4)
        for i, d, m, dist in zip(res["ids"][0], res["documents"][0],
                                 res["metadatas"][0], res["distances"][0]):
            if i not in hits or dist < hits[i][2]:
                hits[i] = (d, m, dist)
    ranked = sorted(hits.values(), key=lambda x: x[2])[:6]
    docs = [r[0] for r in ranked]
    metas = [r[1] for r in ranked]
    dists = [r[2] for r in ranked]

    if not docs or min(dists) > MAX_DISTANCE:
        return FALLBACK, []

    context = "\n\n".join(f"[{m['source']}]\n{d}" for d, m in zip(docs, metas))
    messages = [{"role": "system", "content": SYSTEM}]
    messages += (history or [])[-6:]
    messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"})

    r = llm.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.2,
    )
    reply = r.choices[0].message.content

    # clean lookalike characters the model sometimes outputs
    for ch in ("\u202f", "\u00a0", "\u2009"):
        reply = reply.replace(ch, " ")
    reply = reply.replace("\u2011", "-")

    low = reply.lower().replace("’", "'")
    if "don't have that information" in low or "don't have information" in low:
        return FALLBACK, []

    if re.search(r"\b(he|she|his|her|hers|him)\b", reply, re.IGNORECASE):
        fix = llm.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content":
                "Rewrite this without any gendered pronouns, using names or 'the doctor' instead. "
                f"Change nothing else:\n\n{reply}"}],
            temperature=0,
        )
        reply = fix.choices[0].message.content

    sources = sorted({m["source"] for m, d in zip(metas, dists) if d <= MAX_DISTANCE})
    return reply, sources