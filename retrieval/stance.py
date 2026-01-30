def detect_stance(text: str):
    text = text.lower()

    positive_signals = [
        "benefit", "advantage", "improves",
        "enhances", "effective", "successful"
    ]

    negative_signals = [
        "limitation", "challenge", "drawback",
        "risk", "problem", "inefficient"
    ]

    pos = any(word in text for word in positive_signals)
    neg = any(word in text for word in negative_signals)

    if pos and not neg:
        return "support"
    if neg and not pos:
        return "question"
    if pos and neg:
        return "mixed"
    return "neutral"

def group_by_stance(chunks):
    stance_groups = {
        "support": [],
        "question": [],
        "mixed": [],
        "neutral": []
    }

    for r in chunks:
        stance = detect_stance(r["data"]["text"])
        stance_groups[stance].append(r)

    return stance_groups
