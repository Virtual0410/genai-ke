def has_enough_context(results, min_results=1, min_score=0.35):
    """
    Decide whether retrieved context is strong enough.
    """

    if not results:
        return False

    strong = [
        r for r in results
        if r.get("score", 0) >= min_score
    ]

    return len(strong) >= min_results
