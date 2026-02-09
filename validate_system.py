"""
System validation and health check script.
Tests all components before running queries.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_config():
    """Validate configuration file exists and is valid."""
    print("✓ Checking configuration...")
    try:
        from config import load_config
        config = load_config()
        assert "retrieval" in config
        assert "llm" in config
        assert "embedding" in config
        print("  ✅ config.yaml is valid")
        return True
    except FileNotFoundError:
        print("  ❌ config.yaml not found")
        return False
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        return False

def check_data_files():
    """Check if required data files exist."""
    print("✓ Checking data files...")
    try:
        from config import get_config
        data_file = get_config("data.processed_chunks", "sample_chunks_multi.json")
        data_path = PROJECT_ROOT / "data" / "processed" / data_file
        
        if not data_path.exists():
            print(f"  ❌ Data file not found: {data_path}")
            return False
        
        print(f"  ✅ Data file exists: {data_path}")
        return True
    except Exception as e:
        print(f"  ❌ Data check error: {e}")
        return False

def check_embeddings_cache():
    """Check if embeddings are pre-computed."""
    print("✓ Checking embeddings cache...")
    try:
        from config import get_config
        cache_dir = PROJECT_ROOT / get_config("data.cache_dir", "cache")
        
        if not cache_dir.exists():
            print(f"  ⚠️  No cache directory found: {cache_dir}")
            print("     Run: python precompute_embeddings.py")
            return False
        
        model_name = get_config("embedding.model_name", "all-MiniLM-L6-v2")
        safe_name = model_name.replace('/', '_')
        
        embeddings_file = cache_dir / f"embeddings_{safe_name}.npy"
        metadata_file = cache_dir / f"metadata_{safe_name}.pkl"
        
        if not embeddings_file.exists() or not metadata_file.exists():
            print(f"  ⚠️  Embeddings not pre-computed")
            print("     Run: python precompute_embeddings.py")
            print("     (System will compute on-the-fly, but slower)")
            return False
        
        print(f"  ✅ Embeddings cache found")
        return True
    except Exception as e:
        print(f"  ❌ Cache check error: {e}")
        return False

def check_ollama():
    """Check if Ollama is running and model is available."""
    print("✓ Checking Ollama...")
    try:
        import ollama
        from config import get_config
        
        # Check if Ollama is responsive
        models = ollama.list()
        model_name = get_config("llm.model_name", "mistral")
        
        # Check if required model is available
        available = [m["name"] for m in models.get("models", [])]
        
        if not any(model_name in name for name in available):
            print(f"  ⚠️  Model '{model_name}' not found")
            print(f"     Run: ollama pull {model_name}")
            return False
        
        print(f"  ✅ Ollama running with model: {model_name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Ollama not available: {e}")
        print("     Make sure Ollama is running")
        return False

def check_dependencies():
    """Check if required Python packages are installed."""
    print("✓ Checking dependencies...")
    required = [
        "yaml",
        "numpy",
        "faiss",
        "sentence_transformers",
        "ollama"
    ]
    
    missing = []
    for pkg in required:
        try:
            if pkg == "yaml":
                __import__("yaml")
            else:
                __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"  ❌ Missing packages: {', '.join(missing)}")
        print("     Run: pip install -r requirements.txt")
        return False
    
    print("  ✅ All dependencies installed")
    return True

def run_quick_test():
    """Run a quick end-to-end test."""
    print("✓ Running quick test query...")
    try:
        from pipeline.run_query import run_query
        
        result = run_query("What is machine learning?")
        
        if "error" in result:
            print(f"  ❌ Test query failed: {result['error']}")
            return False
        
        if result["answer"] and len(result["answer"]) > 20:
            print(f"  ✅ Test query successful")
            print(f"     Answer preview: {result['answer'][:80]}...")
            return True
        else:
            print(f"  ⚠️  Test query returned empty/short answer")
            return False
            
    except Exception as e:
        print(f"  ❌ Test query error: {e}")
        return False

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("RAG SYSTEM VALIDATION")
    print("=" * 60)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("Data Files", check_data_files),
        ("Embeddings Cache", check_embeddings_cache),
        ("Ollama Service", check_ollama),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ {name} check crashed: {e}")
            results.append((name, False))
        print()
    
    # Run test query if all checks passed
    critical_checks = results[:5]  # First 5 are critical
    if all(r[1] for r in critical_checks[:4]):  # Embeddings cache is optional
        run_quick_test()
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print()
    if passed == total:
        print("🎉 All checks passed! System ready.")
        return 0
    else:
        print(f"⚠️  {total - passed} check(s) failed. See above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

