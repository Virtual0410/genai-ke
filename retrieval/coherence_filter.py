def filter_by_topic_coherence(query, chunks):
    query_terms = set(query.lower().split())

    filtered = []

    for c in chunks:
        text = c["data"]["text"].lower()
        overlap = sum(1 for word in query_terms if word in text)

        if overlap >= 2:  # minimum relevance threshold
            filtered.append(c)

    return filtered
