def is_trend_query(query: str):
    q = query.lower()
    return any(k in q for k in [
        "future",
        "trend",
        "emerging",
        "next generation",
        "roadmap"
    ])


def filter_for_trend_query(results):

    filtered = []

    for r in results:
        text = r["data"]["text"].lower()

        if any(bad in text for bad in [
            "equation",
            "ψ",
            "confidence interval",
            "regression coefficient",
            "optimizer convergence",
            "boundary value operator"
        ]):
            continue

        filtered.append(r)

    return filtered
