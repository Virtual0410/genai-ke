def evidence_requirement_ok(query: str, selected_chunks: list):

    q = query.lower()

    if "compare" in q or "difference" in q:
        docs = set(c["data"]["doc_id"] for c in selected_chunks)
        return len(docs) >= 2

    if "evaluate" in q or "evaluation" in q:
        text = " ".join(c["data"]["text"].lower() for c in selected_chunks)
        return "metric" in text or "accuracy" in text or "benchmark" in text

    return True
