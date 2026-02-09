"""
Document trust scoring based on type.
"""
from config import get_config

def get_trust_weight(doc_type: str) -> float:
    """
    Return trust weight based on document type.
    Configurable via config.yaml for easy tuning.
    """
    trust_scores = get_config("authority.trust_scores", {
        "research_paper": 1.0,
        "documentation": 0.8,
        "blog": 0.6,
        "note": 0.5
    })
    
    return trust_scores.get(doc_type, 0.5)
