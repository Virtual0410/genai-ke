# retrieval/conflict.py

def detect_conflict(grouped_results, threshold=0.15):
    """
    Detect conflicts when multiple documents have
    similar relevance but different coverage.
    """
    scores = [
        sum(r["score"] for r in chunks) / len(chunks)
        for chunks in grouped_results.values()
    ]

    if len(scores) < 2:
        return False

    scores.sort(reverse=True)

    # If top documents are too close, flag potential conflict
    return abs(scores[0] - scores[1]) < threshold
