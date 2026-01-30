import json
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.retriever import Retriever

# Load chunks
with open("data/processed/sample_chunks_multi.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [c["text"] for c in chunks]
metadata = [
    {
        "chunk_id": c["chunk_id"],
        "text": c["text"],
        "source": c["source"],
        "page": c["page"]
    }
    for c in chunks
]

# Build embeddings + index
embedder = Embedder("all-mpnet-base-v2")
embeddings = embedder.embed_texts(texts)

vector_store = VectorStore(embedding_dim=embeddings.shape[1])
vector_store.add(embeddings, metadata)

# Create retriever
retriever = Retriever(
    embedder=embedder,
    vector_store=vector_store,
    top_k=5,
    score_threshold=0.3
)

# Test query
query = "Explain the evolution of machine learning"
results = retriever.retrieve(query)

print(f"\nQuery: {query}")
print(f"Retrieved {len(results)} chunks\n")

for r in results:
    print(f"Score: {r['score']:.3f}")
    print(f"{r['data']['source']} (page {r['data']['page']})")
    print(r["data"]["text"][:300])
    print("------")
