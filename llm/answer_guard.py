GENERIC_PATTERNS = [
    "as an ai",
    "in general",
    "typically",
    "we can predict",
    "the future will",
    "it is likely",
    "it is expected",
    "generally speaking"
]

def looks_generic(text: str) -> bool:
    text_lower = text.lower()
    return any(p in text_lower for p in GENERIC_PATTERNS)


def enforce_academic_style(answer: str, context: str) -> str:

    if looks_generic(answer):
        return (
            "The generated response contained non-evidence-based generalization. "
            "Based strictly on available sources, only descriptive statements "
            "about the topic can be made."
        )

    return answer