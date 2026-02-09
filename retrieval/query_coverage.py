def query_coverage_ok(query: str, chunks: list) -> bool:

    query = query.lower()

    evaluation_keywords = [
        "evaluate", "evaluation", "benchmark", "metric",
        "measure", "performance", "validation"
    ]

    if any(k in query for k in evaluation_keywords):

        combined_text = " ".join(
            c["data"]["text"].lower()
            for c in chunks
        )

        evidence_words = [
            "metric", "accuracy", "evaluation",
            "benchmark", "experiment", "measure"
        ]

        return any(w in combined_text for w in evidence_words)

    return True
