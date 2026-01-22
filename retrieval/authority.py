# retrieval/authority.py

from retrieval.trust import get_trust_weight
from retrieval.recency import recency_score


def authority_score(doc_stats: dict, doc_meta: dict) -> float:
    """
    Compute final authority score for a document.
    """

    relevance = doc_stats["max_score"]
    trust = get_trust_weight(doc_meta["doc_type"])
    recency = recency_score(doc_meta["published_date"])

    # Weighted blend (EXPLAINABLE)
    return (
        0.5 * relevance +
        0.3 * trust +
        0.2 * recency
    )
