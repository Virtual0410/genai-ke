def build_rag_prompt(query: str, contexts: list) -> str:
    context_text = ""

    for i, c in enumerate(contexts, start=1):
        context_text += f"[Source {i} | Page {c['page']}]\n"
        context_text += c["text"] + "\n\n"

    prompt = f"""
You are a factual assistant.

RULES:
- Answer ONLY using the provided sources.
- If the answer is not contained in the sources, say: "I don't have enough information to answer."
- Cite sources using [Source X].

SOURCES:
{context_text}

QUESTION:
{query}

ANSWER:
"""
    return prompt.strip()
