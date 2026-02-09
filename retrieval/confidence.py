"""
Confidence gating for retrieval results.
"""
from config import get_config

def has_enough_context(results):
    """
    Decide whether retrieved context is strong enough.
    Uses configurable thresholds.
    """
    min_results = get_config("confidence.min_results", 1)
    min_score = get_config("confidence.min_score", 0.45)
    
    if not results:
        return False
    
    strong_results = [
        r for r in results
        if r.get("score", 0) >= min_score
    ]
    
    return len(strong_results) >= min_results
