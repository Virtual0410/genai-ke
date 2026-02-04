import json
from pathlib import Path

from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.retriever import Retriever
from retrieval.keyword_retriever import KeywordRetriever
from retrieval.reranker import rerank
from retrieval.grouping import group_by_document, score_documents
from retrieval.confidence import has_enough_context
from retrieval.context_selector import select_context
from retrieval.stance import group_by_stance
from retrieval.gap_detector import detect_research_gaps
from retrieval.coherence_filter import filter_by_topic_coherence

from retrieval.query_type import requires_synthesis
from retrieval.synthesis import group_chunks_by_source, build_synthesis_context

from llm.context_formatter import format_context
from llm.prompt import SYSTEM_PROMPT
from llm.answer_generator import generate_answer
from llm.report_generator import generate_research_report

from retrieval.authority import authority_score

# Get project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "sample_chunks_multi.json"


def run_query(query: str):

    # ===== LOAD DATA =====
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [c["text"] for c in chunks]
    metadata = [c for c in chunks]   # Full metadata safe

    # ===== EMBEDDINGS =====
    embedder = Embedder("all-MiniLM-L6-v2")
    embeddings = embedder.embed_texts(texts)

    vector_store = VectorStore(embedding_dim=embeddings.shape[1])
    vector_store.add(embeddings, metadata)

    semantic_retriever = Retriever(embedder, vector_store)
    keyword_retriever = KeywordRetriever(metadata)

    # ===== RETRIEVE =====
    semantic_results = semantic_retriever.retrieve(query)
    keyword_results = keyword_retriever.retrieve(query)

    combined = {}

    # Semantic always has full metadata
    for r in semantic_results:
        combined[r["data"]["chunk_id"]] = r

    # Keyword results — patch missing metadata safely
    for r in keyword_results:
        chunk_id = r["chunk_id"]

        if chunk_id not in combined:
            full_meta = next(
                (m for m in metadata if m["chunk_id"] == chunk_id),
                r
            )

            combined[chunk_id] = {
                "score": 0.4,
                "data": full_meta
            }

    final_results = list(combined.values())

    # ===== RERANK =====
    final_results = rerank(final_results, query=query)

    from retrieval.intent_filters import is_trend_query, filter_for_trend_query

    if is_trend_query(query):
        final_results = filter_for_trend_query(final_results)

    if "future" in query.lower() or "trend" in query.lower():
        final_results = [
            r for r in final_results
            if "optimizer" not in r["data"]["text"].lower()
            and "pde" not in r["data"]["text"].lower()
        ]


    # Topic coherence early filter (NEW)
    from retrieval.coherence_filter import filter_by_topic_coherence
    
    final_results = filter_by_topic_coherence(query, final_results)


    # ===== CONFIDENCE CHECK =====
    if not has_enough_context(final_results):
        return {
            "answer": "The available sources do not provide enough evidence to answer this question.",
            "sources": [],
            "report": "Insufficient evidence.",
            "stance": {},
            "context": ""
        }

    # ===== GROUPING =====
    grouped = group_by_document(final_results)
    doc_scores = score_documents(grouped)

    # ===== AUTHORITY =====
    doc_meta = {}

    for r in final_results:
        d = r["data"]

        # Primary key
        doc_meta[d["doc_id"]] = {
            "doc_type": d["doc_type"],
            "published_date": d["published_date"],
            "doc_name": d["doc_name"]
        }

        # Fallback key (prevents KeyError in mixed pipelines)
        doc_meta[d["doc_name"]] = doc_meta[d["doc_id"]]

    doc_authority = {}

    for doc_id, stats in doc_scores.items():
        meta = doc_meta.get(doc_id)

        if meta is None:
            continue

        doc_authority[doc_id] = authority_score(
            stats,
            meta
        )

    # ===== CONTEXT SELECTION =====
    selected_chunks = select_context(
        grouped_results=grouped,
        doc_authority=doc_authority,
        max_docs=2,
        max_chunks_per_doc=3
    )

    if not selected_chunks:
        return {
            "answer": "No trusted context available.",
            "sources": [],
            "report": "Context selection failed.",
            "stance": {},
            "context": ""
        }

    # ===== COHERENCE FILTER =====
    selected_chunks = filter_by_topic_coherence(query, selected_chunks)

    if not selected_chunks:
        return {
            "answer": "No coherent context available.",
            "sources": [],
            "report": "Topic coherence filtering removed all context.",
            "stance": {},
            "context": ""
        }

    # ===== STANCE =====
    stance_groups = group_by_stance(selected_chunks)

    # ===== GAP DETECTION =====
    gap_insights = detect_research_gaps(grouped, stance_groups)

    # ===== CONTEXT FORMAT =====
    context = format_context(selected_chunks)

    # ===== SYNTHESIS =====
    if requires_synthesis(query):
        grouped_chunks = group_chunks_by_source(selected_chunks)
        context = build_synthesis_context(grouped_chunks)

    MIN_CONTEXT_CHARS = 400

    if len(context) < MIN_CONTEXT_CHARS:
        return {
            "answer": "Insufficient grounded context to answer confidently.",
            "sources": [],
            "report": "Context below minimum strength threshold.",
            "stance": stance_groups,
            "context": context
        }

    from retrieval.query_coverage import query_coverage_ok

    if not query_coverage_ok(query, selected_chunks):
        return {
            "answer": "Sources retrieved do not contain required evaluation evidence.",
            "sources": [],
            "report": "Query requires evaluation evidence not present in context.",
            "stance": stance_groups,
            "context": context
        }

    from retrieval.evidence_requirements import evidence_requirement_ok

    if not evidence_requirement_ok(query, selected_chunks):
        return {
            "answer": "Insufficient evidence type for this research question.",
            "sources": [],
            "report": "Evidence requirement policy failed.",
            "stance": stance_groups,
            "context": context
        }

    # ===== ANSWER GENERATION =====
    answer = generate_answer(
        query=query,
        context=context,
        system_prompt=SYSTEM_PROMPT
    )

    from llm.answer_guard import enforce_academic_style

    answer = enforce_academic_style(answer, context)

    from llm.evidence_alignment import enforce_evidence_alignment

    answer = enforce_evidence_alignment(answer, context)

    META_FORBIDDEN = [
    "additional sources should be consulted",
    "for comprehensive understanding",
    "future research should explore",
    "this paper provides valuable insight"
    ]

    # ===== REPORT =====
    report = generate_research_report(
        query=query,
        stance_groups=stance_groups,
        gap_insights=gap_insights,
        selected_chunks=selected_chunks
    )

    # ===== SOURCES =====
    sources = [
        {
            "doc_name": c["data"]["doc_name"],
            "page": c["data"]["page"]
        }
        for c in selected_chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
        "report": report,
        "stance": stance_groups,
        "context": context
    }
