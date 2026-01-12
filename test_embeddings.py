import json
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore

# Load chunks
with open("data/processed/sample_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [c["text"] for c in chunks]
metadata = [
    {
        "chunk_id": c["chunk_id"],
        "source": c["source"],
        "page": c["page"],
        "text": c["text"]
    }
    for c in chunks
]

# Base embedding model
model_name = "all-mpnet-base-v2"
embedder = Embedder(model_name)

embeddings = embedder.embed_texts(texts)

vector_store = VectorStore(embedding_dim=embeddings.shape[1])
vector_store.add(embeddings, metadata)

print(f"Indexed {len(metadata)} chunks using {model_name}")

# Test query
query = "Explain the evolution of machine learning"
query_embedding = embedder.embed_texts([query])

results = vector_store.search(query_embedding, top_k=3)

for r in results:
    print(f"\nScore: {r['score']}")
    print(f"{r['data']['source']} (page {r['data']['page']})")
    print(r["data"]["text"][:300])
