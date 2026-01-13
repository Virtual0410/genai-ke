def rerank(results, query=None, min_len=50, max_len=800):
    reranked = []
    query_lower = query.lower() if query else ""

    for r in results:
        text = r["data"]["text"]
        score = r.get("score", 0.5)
        length = len(text)
        text_lower = text.lower()

        if length < min_len:
            score *= 0.5

        if length > max_len:
            score *= 0.8

        if query_lower:
            if "future" in query_lower and "future" in text_lower:
                score *= 1.3
            if "trend" in query_lower and "trend" in text_lower:
                score *= 1.2

        if query_lower and ("future" in query_lower or "trend" in query_lower):
            if "abstract" in text_lower or "introduction" in text_lower:
                score *= 0.6

        reranked.append({
            "score": score,
            "data": r["data"]
        })

    reranked.sort(key=lambda x: x["score"], reverse=True)
    return reranked
