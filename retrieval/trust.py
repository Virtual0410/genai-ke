# retrieval/trust.py

TRUST_WEIGHTS = {
    "research_paper": 1.0,
    "blog": 0.7,
    "notes": 0.4
}


def get_trust_weight(doc_type: str) -> float:
    """
    Return trust weight based on document type.
    """
    return TRUST_WEIGHTS.get(doc_type, 0.3)
