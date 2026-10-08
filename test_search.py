import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
col = chromadb.PersistentClient(path="db").get_collection("faq")

question = input("Ask a question: ")
res = col.query(query_embeddings=[model.encode(question).tolist()], n_results=2)

for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
    print("\n---", meta["source"], "| distance:", round(dist, 3))
    print(doc)