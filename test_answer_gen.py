"""
Test answer_generator directly with ollama library
"""
import ollama

query = "What future trends in machine learning are discussed?"
context = """
[1] Machine learning future trends include:
- Explainable AI models
- Federated learning
- Transfer learning
- Integration with IoT and blockchain

[2] Future developments:
- Enhanced privacy through federated learning
- Better model interpretability
- Cross-domain transfer learning
"""

system_prompt = "You are a factual research assistant. Answer using only the provided context."

full_prompt = f"""
{system_prompt}

Context:
{context}

Question:
{query}

Answer based only on the context above.
"""

print("Testing ollama.chat() directly...")
print(f"Query: {query}\n")

try:
    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are an academic research assistant."},
            {"role": "user", "content": full_prompt}
        ]
    )
    
    answer = response["message"]["content"]
    print(f"Success!\nAnswer: {answer}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
