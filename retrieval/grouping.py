"""
Document grouping utilities.
"""
from collections import defaultdict

def group_by_document(results):
    """
    Group retrieval results by document ID.
    """
    grouped = defaultdict(list)

    for r in results:
        # Use doc_id as primary key, fallback to source
        doc_id = r["data"].get("doc_id") or r["data"].get("source")
        if doc_id:
            grouped[doc_id].append(r)

    return dict(grouped)

def score_documents(grouped_results):
    """
    Compute document-level score based on chunk scores.
    """
    doc_scores = {}

    for doc_id, chunks in grouped_results.items():
        scores = [r["score"] for r in chunks]
        doc_scores[doc_id] = {
            "max_score": max(scores),
            "avg_score": sum(scores) / len(scores),
            "chunk_count": len(scores)
        }

    return doc_scores
