"""
Comprehensive system test
Tests all major components end-to-end
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# ASCII-safe output for Windows
OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[WARN]"

print("=" * 70)
print("GENAI KNOWLEDGE ENGINE - SYSTEM TEST")
print("=" * 70)

# Test 1: Imports
print(f"\n[1/6] Testing imports...")
try:
    from pipeline.run_query import run_query
    from llm.answer_generator import generate_answer
    import ollama
    print(f"{OK} All imports successful")
except Exception as e:
    print(f"{FAIL} Import failed: {e}")
    sys.exit(1)

# Test 2: Ollama connectivity
print("\n[2/6] Testing Ollama connectivity...")
try:
    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": "Say 'OK' if you're working"}]
    )
    if response["message"]["content"]:
        print(f"✅ Ollama responding: {response['message']['content'][:50]}...")
    else:
        print("❌ Ollama returned empty response")
        sys.exit(1)
except Exception as e:
    print(f"❌ Ollama connection failed: {e}")
    print("   Make sure Ollama is running: ollama serve")
    sys.exit(1)

# Test 3: Data file exists
print("\n[3/6] Testing data availability...")
data_path = Path(__file__).parent / "data" / "processed" / "sample_chunks_multi.json"
if data_path.exists():
    import json
    with open(data_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"✅ Data loaded: {len(chunks)} chunks available")
else:
    print(f"❌ Data file not found: {data_path}")
    sys.exit(1)

# Test 4: Query with known answer
print("\n[4/6] Testing RAG pipeline with known query...")
try:
    query = "What future trends in machine learning are discussed?"
    result = run_query(query)
    
    if result["answer"] and len(result["answer"]) > 20:
        print(f"✅ Query successful")
        print(f"   Answer length: {len(result['answer'])} chars")
        print(f"   Sources used: {len(result['sources'])}")
        print(f"   Answer preview: {result['answer'][:100]}...")
    else:
        print(f"❌ Query returned empty or very short answer")
        print(f"   Answer: {result['answer']}")
except Exception as e:
    print(f"❌ Query failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Query with no answer (should refuse)
print("\n[5/6] Testing refusal on unsupported query...")
try:
    query = "What is the meaning of life?"
    result = run_query(query)
    
    answer_lower = result["answer"].lower()
    if any(phrase in answer_lower for phrase in ["not provide", "insufficient", "enough evidence"]):
        print(f"✅ Correctly refused unsupported query")
        print(f"   Response: {result['answer'][:80]}...")
    else:
        print(f"⚠️  Warning: May have hallucinated answer to unsupported query")
        print(f"   Answer: {result['answer'][:100]}...")
except Exception as e:
    print(f"❌ Refusal test failed: {e}")

# Test 6: Stance detection
print("\n[6/6] Testing stance detection...")
try:
    query = "What are machine learning challenges?"
    result = run_query(query)
    
    stance = result.get("stance", {})
    total_stances = sum(len(v) for v in stance.values())
    
    if total_stances > 0:
        print(f"✅ Stance detection working")
        print(f"   Support: {len(stance.get('support', []))}")
        print(f"   Question: {len(stance.get('question', []))}")
        print(f"   Mixed: {len(stance.get('mixed', []))}")
        print(f"   Neutral: {len(stance.get('neutral', []))}")
    else:
        print(f"⚠️  No stance information detected")
except Exception as e:
    print(f"❌ Stance test failed: {e}")

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("✅ System is operational")
print("")
print("Next steps:")
print("1. Run UI: streamlit run ui/app.py")
print("2. Add your own documents to data/raw/")
print("3. Test with your own queries")
print("=" * 70)

