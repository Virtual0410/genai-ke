"""
Main query execution pipeline with caching and error handling.
"""
import json
import pickle
import numpy as np
from pathlib import Path
from typing import Optional

from config import get_config, load_config
from errors import DataLoadError, EmbeddingError, RetrievalError, LLMError

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
from retrieval.authority import authority_score

from llm.context_formatter import format_context
from llm.prompt import SYSTEM_PROMPT
from llm.answer_generator import generate_answer
from llm.report_generator import generate_research_report

# Global cache for loaded data
_CACHE = {
    "embeddings": None,
    "metadata": None,
    "vector_store": None,
    "semantic_retriever": None,
    "keyword_retriever": None,
    "embedder": None
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"
DATA_DIR = PROJECT_ROOT / "data" / "processed"

def _load_embeddings_and_metadata():
    """
    Load pre-computed embeddings and metadata from cache.
    Falls back to computing on-the-fly if cache doesn't exist.
    """
    global _CACHE
    
    if _CACHE["embeddings"] is not None and _CACHE["metadata"] is not None:
        return _CACHE["embeddings"], _CACHE["metadata"]
    
    model_name = get_config("embedding.model_name", "all-MiniLM-L6-v2")
    safe_model_name = model_name.replace('/', '_')
    
    embeddings_path = CACHE_DIR / f"embeddings_{safe_model_name}.npy"
    metadata_path = CACHE_DIR / f"metadata_{safe_model_name}.pkl"
    
    try:
        if embeddings_path.exists() and metadata_path.exists():
            # Load from cache
            print(f"Loading embeddings from cache: {embeddings_path}")
            embeddings = np.load(embeddings_path)
            
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            
            _CACHE["embeddings"] = embeddings
            _CACHE["metadata"] = metadata
            
            return embeddings, metadata
        else:
            # Cache doesn't exist - compute on-the-fly
            print("⚠️  No embedding cache found. Computing embeddings...")
            print(f"   Run 'python precompute_embeddings.py' to speed up future queries.")
            
            data_file = get_config("data.processed_chunks", "sample_chunks_multi.json")
            data_path = DATA_DIR / data_file
            
            if not data_path.exists():
                raise DataLoadError(f"Data file not found: {data_path}")
            
            with open(data_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            
            texts = [c["text"] for c in chunks]
            
            embedder = Embedder(model_name)
            embeddings = embedder.embed_texts(texts)
            
            _CACHE["embeddings"] = embeddings
            _CACHE["metadata"] = chunks
            
            return embeddings, chunks
            
    except Exception as e:
        raise EmbeddingError(f"Failed to load embeddings: {str(e)}")

def _get_retrievers():
    """
    Get or initialize retrieval components with caching.
    """
    global _CACHE
    
    if _CACHE["semantic_retriever"] and _CACHE["keyword_retriever"]:
        return _CACHE["semantic_retriever"], _CACHE["keyword_retriever"]
    
    try:
        embeddings, metadata = _load_embeddings_and_metadata()
        
        # Initialize vector store
        if _CACHE["vector_store"] is None:
            vector_store = VectorStore(embedding_dim=embeddings.shape[1])
            vector_store.add(embeddings, metadata)
            _CACHE["vector_store"] = vector_store
        
        # Initialize embedder
        if _CACHE["embedder"] is None:
            model_name = get_config("embedding.model_name", "all-MiniLM-L6-v2")
            _CACHE["embedder"] = Embedder(model_name)
        
        # Initialize retrievers
        semantic_retriever = Retriever(_CACHE["embedder"], _CACHE["vector_store"])
        keyword_retriever = KeywordRetriever(metadata)
        
        _CACHE["semantic_retriever"] = semantic_retriever
        _CACHE["keyword_retriever"] = keyword_retriever
        
        return semantic_retriever, keyword_retriever
        
    except Exception as e:
        raise RetrievalError(f"Failed to initialize retrievers: {str(e)}")

def run_query(query: str) -> dict:
    """
    Execute full RAG pipeline for a query.
    
    Args:
        query: User question
    
    Returns:
        dict with answer, sources, report, stance, context
    """
    try:
        # Load config
        load_config()
        
        # Get retrievers (cached)
        semantic_retriever, keyword_retriever = _get_retrievers()
        
        # ===== RETRIEVE =====
        semantic_top_k = get_config("retrieval.semantic_top_k", 10)
        keyword_top_k = get_config("retrieval.keyword_top_k", 5)
        
        semantic_results = semantic_retriever.retrieve(query, top_k=semantic_top_k)
        keyword_results = keyword_retriever.retrieve(query, top_k=keyword_top_k)
        
        # ===== MERGE RESULTS =====
        combined = {}
        
        for r in semantic_results:
            combined[r["data"]["chunk_id"]] = r
        
        for r in keyword_results:
            chunk_id = r.get("chunk_id")
            if chunk_id and chunk_id not in combined:
                combined[chunk_id] = {
                    "score": r.get("score", 0.4),
                    "data": r
                }
        
        final_results = list(combined.values())
        
        if not final_results:
            return {
                "answer": "No relevant information found for this query.",
                "sources": [],
                "report": "Retrieval returned no results.",
                "stance": {},
                "context": ""
            }
        
        # ===== RERANK =====
        final_results = rerank(final_results, query=query)
        
        # ===== COHERENCE FILTER =====
        final_results = filter_by_topic_coherence(query, final_results)
        
        # ===== CONFIDENCE CHECK =====
        if not has_enough_context(final_results):
            return {
                "answer": "The available sources do not provide enough evidence to answer this question.",
                "sources": [],
                "report": "Insufficient retrieval confidence.",
                "stance": {},
                "context": ""
            }
        
        # ===== GROUPING =====
        grouped = group_by_document(final_results)
        doc_scores = score_documents(grouped)
        
        # ===== AUTHORITY SCORING =====
        metadata = _CACHE["metadata"]
        doc_meta = {}
        
        for r in final_results:
            d = r["data"]
            doc_id = d.get("doc_id")
            if doc_id:
                doc_meta[doc_id] = {
                    "doc_type": d.get("doc_type", "unknown"),
                    "published_date": d.get("published_date", "unknown"),
                    "doc_name": d.get("doc_name", "unknown")
                }
        
        doc_authority = {}
        for doc_id, stats in doc_scores.items():
            meta = doc_meta.get(doc_id)
            if meta:
                try:
                    doc_authority[doc_id] = authority_score(stats, meta)
                except Exception as e:
                    # Fallback to just using relevance if authority scoring fails
                    doc_authority[doc_id] = stats["max_score"]
        
        # If no authority scores computed, use all documents
        if not doc_authority:
            for doc_id in grouped.keys():
                doc_authority[doc_id] = 1.0
        
        # ===== CONTEXT SELECTION =====
        selected_chunks = select_context(grouped, doc_authority)
        
        if not selected_chunks:
            # Fallback: If authority filtering is too strict, just use top chunks by score
            print("⚠️  Authority filtering too strict, using top chunks by relevance...")
            all_chunks = []
            for chunks in grouped.values():
                all_chunks.extend(chunks)
            all_chunks.sort(key=lambda x: x["score"], reverse=True)
            max_chunks = get_config("context_selection.max_docs", 3) * get_config("context_selection.max_chunks_per_doc", 4)
            selected_chunks = all_chunks[:max_chunks]
            
        if not selected_chunks:
            return {
                "answer": "No context available after filtering.",
                "sources": [],
                "report": "Context selection produced no results even with fallback.",
                "stance": {},
                "context": ""
            }
        
        # ===== COHERENCE FILTER (AGAIN ON SELECTED) =====
        selected_chunks = filter_by_topic_coherence(query, selected_chunks)
        
        if not selected_chunks:
            return {
                "answer": "No coherent context available after filtering.",
                "sources": [],
                "report": "Coherence filtering removed all context.",
                "stance": {},
                "context": ""
            }
        
        # ===== STANCE DETECTION =====
        stance_groups = group_by_stance(selected_chunks)
        
        # ===== GAP DETECTION =====
        gap_insights = detect_research_gaps(grouped, stance_groups)
        
        # ===== CONTEXT FORMATTING =====
        if requires_synthesis(query):
            grouped_chunks = group_chunks_by_source(selected_chunks)
            context = build_synthesis_context(grouped_chunks)
        else:
            context = format_context(selected_chunks)
        
        # ===== MINIMUM CONTEXT CHECK =====
        min_context_chars = get_config("confidence.min_context_chars", 300)
        if len(context) < min_context_chars:
            return {
                "answer": "Insufficient grounded context to answer confidently.",
                "sources": [],
                "report": "Context below minimum length threshold.",
                "stance": stance_groups,
                "context": context
            }
        
        # ===== ANSWER GENERATION =====
        try:
            answer = generate_answer(
                query=query,
                context=context,
                system_prompt=SYSTEM_PROMPT
            )
        except Exception as e:
            raise LLMError(f"Answer generation failed: {str(e)}")
        
        # ===== RESEARCH REPORT =====
        report = generate_research_report(
            query=query,
            stance_groups=stance_groups,
            gap_insights=gap_insights,
            selected_chunks=selected_chunks
        )
        
        # ===== SOURCES =====
        sources = [
            {
                "doc_name": c["data"].get("doc_name", "unknown"),
                "page": c["data"].get("page", "unknown")
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
        
    except (DataLoadError, EmbeddingError, RetrievalError, LLMError) as e:
        # Known RAG errors - return structured error response
        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "report": f"Pipeline error: {type(e).__name__}",
            "stance": {},
            "context": "",
            "error": str(e)
        }
    
    except Exception as e:
        # Unknown error - still return structured response
        return {
            "answer": f"Unexpected error: {str(e)}",
            "sources": [],
            "report": "Unknown error occurred",
            "stance": {},
            "context": "",
            "error": str(e)
        }

def clear_cache():
    """Clear the query pipeline cache. Useful for testing."""
    global _CACHE
    _CACHE = {
        "embeddings": None,
        "metadata": None,
        "vector_store": None,
        "semantic_retriever": None,
        "keyword_retriever": None,
        "embedder": None
    }
