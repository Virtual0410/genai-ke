from llm.ollama_llm import OllamaLLM
from config_loader import get_config


def generate_answer(query, context, system_prompt):
    """
    Generate a grounded answer using the local LLM with improved prompting.
    Now uses unified Ollama interface.
    """

    full_prompt = f"""
{system_prompt}

CONTEXT PROVIDED:
{context}

QUESTION:
{query}

CRITICAL INSTRUCTIONS:
1. Answer ONLY using the context above. Do not use external knowledge.
2. Cite sources using [number] format (e.g., [1], [2]).
3. Be direct and specific. No speculation or general statements.
4. If the context lacks sufficient evidence, respond with:
   "The available sources do not provide enough evidence to answer this question."
5. Do NOT include:
   - Reasoning exercises or examples beyond the context
   - Phrases like "typically", "generally", "in most cases"
   - Future predictions unless explicitly stated in sources
   - Comparisons not supported by the context

RESPONSE FORMAT:
- Start directly with the answer (no preamble like "Based on the sources...")
- Keep answer concise and factual
- End with relevant citations

ANSWER:
"""

    try:
        # Use unified Ollama interface
        llm = OllamaLLM()
        answer = llm.generate(
            prompt=full_prompt,
            system_prompt="You are a precise academic research assistant. Provide only evidence-based answers from the given context. Never speculate or add external knowledge."
        )
        
        # Post-processing: Remove common LLM hedging phrases
        hedges_to_remove = [
            "Based on the provided context, ",
            "According to the sources, ",
            "The context suggests that ",
            "From the information given, ",
        ]
        
        for hedge in hedges_to_remove:
            if answer.startswith(hedge):
                answer = answer[len(hedge):]
                break
        
        return answer
        
    except Exception as e:
        error_msg = str(e)
        return f"Error generating answer: {error_msg}\n\nPlease check that Ollama is running with: ollama list"
