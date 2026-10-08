import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
col = chromadb.PersistentClient(path="db").get_collection("faq")

# (question, can the docs answer it?)
tests = [
    ("What are your timings?", True),
    ("What time does the clinic open?", True),
    ("Are you open on Sundays?", True),
    ("How much does the dermatologist cost?", True),
    ("Do you take UPI?", True),
    ("Which doctor sees kids?", True),
    ("Where are you located?", True),
    ("What is your phone number?", True),
    ("Do you have a pharmacy?", False),
    ("Does Dr. Mehta do home visits?", False),
    ("What is the capital of France?", False),
    ("What medicine should I take for fever?", False),
]

def best(q, prefix):
    emb = model.encode(prefix + q).tolist()
    return col.query(query_embeddings=[emb], n_results=1)["distances"][0][0]

for prefix in ["", "Sunrise Health Clinic: "]:
    print(f"\n=== prefix: {prefix!r} ===")
    yes, no = [], []
    for q, ok in tests:
        d = best(q, prefix)
        (yes if ok else no).append(d)
        print(f"{d:.3f} | {'ANSWERABLE  ' if ok else 'unanswerable'} | {q}")
    print(f"Worst answerable: {max(yes):.3f} | Best unanswerable: {min(no):.3f}")
    print("-> clean gap, a threshold works" if max(yes) < min(no)
          else "-> OVERLAP, distance alone cannot separate these")