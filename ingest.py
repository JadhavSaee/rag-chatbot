import os, glob
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
db = chromadb.PersistentClient(path="db")
col = db.get_or_create_collection("faq", metadata={"hnsw:space": "cosine"})

def chunk(text, size=250, overlap=50):
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + size])
        i += size - overlap
    return out

def add_text(text, source, page):
    pieces = text.split("\n\n") if source.endswith(".txt") else chunk(text)
    for n, c in enumerate(pieces):
        if c.strip():
            col.upsert(
                ids=[f"{source}-{page}-{n}"],
                documents=[c.strip()],
                embeddings=[model.encode(c).tolist()],
                metadatas=[{"source": source, "page": page}],
            )

for path in glob.glob("docs/*"):
    name = os.path.basename(path)
    if path.endswith(".pdf"):
        for p, page in enumerate(PdfReader(path).pages):
            add_text(page.extract_text() or "", name, p + 1)
    elif path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            add_text(f.read(), name, 1)

print("Done:", col.count(), "chunks")