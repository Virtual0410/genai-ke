import json
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.retriever import Retriever
from retrieval.keyword_retriever import KeywordRetriever

# Load chunks
with open("data/processed/sample_chunks.json", "r", encoding="utf-8") as f:
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

# Semantic setup
embedder = Embedder("all-MiniLM-L6-v2")
embeddings = embedder.embed_texts(texts)

vector_store = VectorStore(embedding_dim=embeddings.shape[1])
vector_store.add(embeddings, metadata)

semantic_retriever = Retriever(embedder, vector_store)

# Keyword setup
keyword_retriever = KeywordRetriever(metadata)

query = "What future trends in machine learning are discussed?"

semantic_results = semantic_retriever.retrieve(query)
keyword_results = keyword_retriever.retrieve(query)

combined = {}

for r in semantic_results:
    combined[r["data"]["chunk_id"]] = r

for r in keyword_results:
    chunk_id = r["chunk_id"]

    if chunk_id not in combined:
        combined[chunk_id] = {
            "score": 0.4, 
            "data": {
                "chunk_id": r["chunk_id"],
                "text": r["text"],
                "source": r["source"],
                "page": r["page"]
            }
        }

final_results = list(combined.values())


from retrieval.reranker import rerank

final_results = rerank(final_results, query=query)

from retrieval.confidence import has_enough_context
if not has_enough_context(final_results):
    print("NO CONTEXT — refusing to answer")
    exit()

print(f"\nHybrid results for: {query}\n")
for r in final_results:
    print(f"{r['data']['source']} (page {r['data']['page']})")
    print(f"Score: {r['score']:.3f}")
    print(r["data"]["text"][:300])
    print("------")

