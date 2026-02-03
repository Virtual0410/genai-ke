import ollama


def generate_answer(query, context, system_prompt):
    """
    Generate a grounded answer using the local LLM.
    """

    full_prompt = f"""
{system_prompt}

Context:
{context}

Question:
{query}

Instructions:
- Answer ONLY using the provided context.
- Cite sources using [number] format.
- If evidence is weak or missing, say:
  "The available sources do not provide enough evidence to answer this question."
"""

    response = ollama.chat(
        model="phi:2.7b",
        messages=[
            {"role": "system", "content": "You are an academic research assistant."},
            {"role": "user", "content": full_prompt}
        ]
    )

    return response["message"]["content"]
