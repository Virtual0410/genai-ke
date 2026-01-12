from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
import numpy as np
import json

def load_chunks(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


chunks = load_chunks("data/processed/sample_chunks.json")

models = [
    "all-MiniLM-L6-v2",
    "all-mpnet-base-v2",
    "multi-qa-MiniLM-L6-cos-v1",
]

queries = [
    "What is machine learning?",
    "Explain the evolution of machine learning.",
    "What are the main types of machine learning?",
    "What are the applications of machine learning?",
    "What is API?",
    "What future trends in machine learning are discussed?"
]

for model_name in models:
    print("\n" + "=" * 70)
    print(f"MODEL: {model_name}")

    embedder = Embedder(model_name=model_name)

    texts = [c["text"] for c in chunks]
    chunk_embeddings = embedder.embed_texts(texts)

    # Initialize vector store
    store = VectorStore(embedding_dim=chunk_embeddings.shape[1])
    store.add(chunk_embeddings, chunks)

    for query in queries:
        print("\n" + "-" * 50)
        print(f"QUERY: {query}")

        # Embed query
        query_embedding = embedder.embed_texts([query])

        results = store.search(query_embedding, top_k=3)

        if not results or results[0]["score"] < 0.30:
            print("❌ NO ANSWER IN DOCUMENT")
            continue

        for r in results:
            print(f"\nScore: {r['score']:.4f}")
            print(f"{r['data']['source']} (page {r['data']['page']})")
            print(r["data"]["text"][:200], "...")
