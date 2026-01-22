import json

from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.retriever import Retriever
from retrieval.keyword_retriever import KeywordRetriever
from retrieval.reranker import rerank
from retrieval.grouping import group_by_document, score_documents
from retrieval.confidence import has_enough_context


with open("data/processed/sample_chunks_multi.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [c["text"] for c in chunks]

metadata = [
    {
        "chunk_id": c["chunk_id"],
        "doc_id": c["doc_id"],
        "doc_name": c["doc_name"],
        "doc_type": c["doc_type"],
        "published_date": c["published_date"],
        "text": c["text"],
        "source": c["source"],
        "page": c["page"],
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

# Merge semantic + keyword 

combined = {}

for r in semantic_results:
    combined[r["data"]["chunk_id"]] = r

for r in keyword_results:
    chunk_id = r["chunk_id"]

    if chunk_id not in combined:
        combined[chunk_id] = {
            "score": 0.4, 
            "data": r     
        }

final_results = list(combined.values())

# Reranking

final_results = rerank(final_results, query=query)

# Confidence gate 

if not has_enough_context(final_results):
    print("NO CONTEXT — refusing to answer")
    exit()

# Document-level grouping

grouped = group_by_document(final_results)
doc_scores = score_documents(grouped)

from retrieval.authority import authority_score
from retrieval.conflict import detect_conflict

# Build document metadata map
doc_meta = {}
for r in final_results:
    d = r["data"]
    doc_meta[d["doc_id"]] = {
        "doc_type": d["doc_type"],
        "published_date": d["published_date"],
        "doc_name": d["doc_name"]
    }

# Compute authority scores
doc_authority = {}
for doc_id, stats in doc_scores.items():
    doc_authority[doc_id] = authority_score(
        stats,
        doc_meta[doc_id]
    )

print("\nDocument authority ranking:\n")

for doc_id, score in sorted(
    doc_authority.items(),
    key=lambda x: x[1],
    reverse=True
):
    meta = doc_meta[doc_id]
    print(f"{doc_id} ({meta['doc_type']}, {meta['published_date']}): {score:.3f}")


if detect_conflict(grouped):
    print("\n⚠️  Potential conflict detected between sources.")


# Output

print("\nDocument-level summary:\n")

for doc_id, stats in doc_scores.items():
    print(f"{doc_id}:")
    print(f"  max_score   = {stats['max_score']:.3f}")
    print(f"  avg_score   = {stats['avg_score']:.3f}")
    print(f"  chunk_count = {stats['chunk_count']}")
    print()

print(f"\nHybrid results for: {query}\n")

for r in final_results:
    print(f"{r['data']['source']} (page {r['data']['page']})")
    print(f"Score: {r['score']:.3f}")
    print(r["data"]["text"][:300])
    print("------")
