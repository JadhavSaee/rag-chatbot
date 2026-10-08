from rag import answer, col, model

qs = [("Do you take UPI?", "upi"),
      ("Where are you located?", "mg road"),
      ("What is the cancellation policy?", "4 hours")]

for q, kw in qs:
    print("\n=====", q)
    emb = model.encode("Sunrise Health Clinic: " + q).tolist()
    res = col.query(query_embeddings=[emb], n_results=4)
    for d, doc in zip(res["distances"][0], res["documents"][0]):
        print(f"  {d:.3f} | {doc[:60]!r}")
    for i in range(3):
        reply, _ = answer(q)
        print(f"  run {i+1}: {reply!r}")
        print("     keyword found:", kw in reply.lower())