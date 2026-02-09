"""
Authority scoring for documents.
"""
from retrieval.trust import get_trust_weight
from retrieval.recency import recency_score
from config import get_config

def authority_score(doc_stats: dict, doc_meta: dict) -> float:
    """
    Compute final authority score for a document.
    Uses configurable weights for interpretability.
    """
    relevance = doc_stats["max_score"]
    trust = get_trust_weight(doc_meta["doc_type"])
    recency = recency_score(doc_meta["published_date"])
    
    # Get weights from config
    rel_weight = get_config("authority.relevance_weight", 0.5)
    trust_weight = get_config("authority.trust_weight", 0.3)
    rec_weight = get_config("authority.recency_weight", 0.2)
    
    # Weighted blend (explicit and tunable)
    return (
        rel_weight * relevance +
        trust_weight * trust +
        rec_weight * recency
    )
