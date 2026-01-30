import json
from retrieval.query_type import requires_synthesis
from retrieval.synthesis import group_chunks_by_source, build_synthesis_context
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.retriever import Retriever
from retrieval.keyword_retriever import KeywordRetriever
from retrieval.reranker import rerank
from retrieval.grouping import group_by_document, score_documents
from retrieval.confidence import has_enough_context
from retrieval.context_selector import select_context
from llm.context_formatter import format_context
from llm.prompt import SYSTEM_PROMPT
from retrieval.stance import detect_stance, group_by_stance
from retrieval.gap_detector import detect_research_gaps
from llm.report_generator import generate_research_report
from retrieval.coherence_filter import filter_by_topic_coherence

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

query = "Do papers compare federated learning drawbacks?"

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

selected_chunks = select_context(
    grouped_results=grouped,
    doc_authority=doc_authority,
    max_docs=2,
    max_chunks_per_doc=3
)

if not selected_chunks:
    print("NO TRUSTED CONTEXT — refusing to generate answer")
    exit()

# ✅ MOVED HERE — COHERENCE FILTER (ONLY REORDERED)
selected_chunks = filter_by_topic_coherence(query, selected_chunks)

if not selected_chunks:
    print("NO COHERENT CONTEXT — refusing to generate answer")
    exit()

# --- Synthesis Logic ---
if requires_synthesis(query):
    grouped_chunks = group_chunks_by_source(selected_chunks)
    synthesis_context = build_synthesis_context(grouped_chunks)
    print("\nSynthesis Context Built:\n")
    print(synthesis_context)

# --- Stance Detection ---
stance_groups = group_by_stance(selected_chunks)

print("\nStance Summary:\n")
for stance, items in stance_groups.items():
    print(f"{stance}: {len(items)} sources")

gap_insights = detect_research_gaps(grouped, stance_groups)

print("\nResearch Gap Signals:\n")
for insight in gap_insights:
    print("-", insight)

report = generate_research_report(
    query=query,
    stance_groups=stance_groups,
    gap_insights=gap_insights,
    selected_chunks=selected_chunks
)

print("\nAcademic Insight Report:\n")
print(report)

# --- Final Context Formatting ---
context = format_context(selected_chunks)

print("\nFinal context passed to LLM:\n")
print(context)
