def extract_trend_keywords(context: str):

    keywords = []

    if "explainable" in context.lower():
        keywords.append("Explainable AI")

    if "federated" in context.lower():
        keywords.append("Federated Learning")

    if "physics" in context.lower() and "future" in context.lower():
        keywords.append("Physics-informed ML")

    return keywords


def enforce_evidence_alignment(answer: str, context: str):

    allowed = extract_trend_keywords(context)

    answer_lower = answer.lower()

    violations = []

    if "physics-informed" in answer_lower and "Physics-informed ML" not in allowed:
        violations.append("physics-informed ML")

    if violations:
        return (
            "The generated answer referenced concepts not clearly supported by the retrieved evidence. "
            "Based strictly on available sources, only explicitly mentioned future trends should be reported."
        )

    return answer
