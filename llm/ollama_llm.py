"""
Unified Ollama LLM interface using the official SDK.
Removed subprocess-based implementation.
"""
import ollama
from config import get_config

class OllamaLLM:
    """
    Ollama LLM interface using official Python SDK.
    """
    
    def __init__(self, model_name=None):
        self.model_name = model_name or get_config("llm.model_name", "mistral")
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate completion using Ollama chat interface.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for instructions
        
        Returns:
            Generated text response
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": get_config("llm.temperature", 0.1),
                    "num_predict": get_config("llm.max_tokens", 400),
                    "top_p": get_config("llm.top_p", 0.9),
                }
            )
            
            return response["message"]["content"].strip()
            
        except Exception as e:
            error_msg = (
                f"Ollama error: {str(e)}\n\n"
                f"Please ensure Ollama is running:\n"
                f"  1. Check: ollama list\n"
                f"  2. Pull model if needed: ollama pull {self.model_name}\n"
                f"  3. Test: ollama run {self.model_name}"
            )
            return error_msg
    
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            ollama.list()
            return True
        except:
            return False
