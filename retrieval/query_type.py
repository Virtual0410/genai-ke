def requires_synthesis(query: str) -> bool:
    keywords = [
        "compare",
        "contrast",
        "across",
        "difference",
        "relationship",
        "synthesize",
        "combine"
    ]

    query_lower = query.lower()
    return any(k in query_lower for k in keywords)
