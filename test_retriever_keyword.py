import json
from retrieval.keyword_retriever import KeywordRetriever

with open("data/processed/sample_chunks_multi.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

retriever = KeywordRetriever(chunks)

query = "FAISS index architecture"
results = retriever.retrieve(query, top_k=5)

print(f"\nKeyword results for: {query}\n")
for r in results:
    print(r["text"][:300])
    print("------")
