"""
Direct test of Ollama with UTF-8 encoding
"""
import subprocess

prompt = "What is machine learning? Answer in one sentence."

print("Testing Ollama with UTF-8 encoding...")
print(f"Prompt: {prompt}\n")

result = subprocess.run(
    ["ollama", "run", "mistral"],
    input=prompt.encode('utf-8'),
    capture_output=True
)

output = result.stdout.decode('utf-8', errors='replace').strip()
error = result.stderr.decode('utf-8', errors='replace').strip()

# Windows terminal workaround - replace problematic chars before printing
print(f"Output: {output.encode('ascii', errors='replace').decode('ascii')}")
print(f"Error: {error.encode('ascii', errors='replace').decode('ascii')}")
print(f"Return code: {result.returncode}")
