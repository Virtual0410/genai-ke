import subprocess


class OllamaLLM:
    def __init__(self, model_name="mistral"):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        result = subprocess.run(
            ["ollama", "run", self.model_name],
            input=prompt,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
