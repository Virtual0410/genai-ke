#!/usr/bin/env python3
"""
Integration test for the full RAG pipeline
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline.run_query import run_query
import json


def test_query(query: str):
    """Test a single query"""
    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print('='*80)
    
    try:
        result = run_query(query)
        
        print(f"\n📘 ANSWER:")
        print(result['answer'])
        
        print(f"\n📚 SOURCES ({len(result['sources'])} total):")
        unique_sources = list(set(
            (s['doc_name'], s['page']) for s in result['sources']
        ))
        for doc, page in unique_sources:
            print(f"  - {doc} (page {page})")
        
        print(f"\n⚖️ EVIDENCE PERSPECTIVE:")
        stance = result['stance']
        print(f"  Support: {len(stance.get('support', []))}")
        print(f"  Question: {len(stance.get('question', []))}")
        print(f"  Mixed: {len(stance.get('mixed', []))}")
        print(f"  Neutral: {len(stance.get('neutral', []))}")
        
        print(f"\n✅ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run multiple test queries"""
    
    test_queries = [
        "What future trends in machine learning are discussed?",
        "What are the challenges in machine learning?",
        "How is machine learning applied in healthcare?",
        "What is explainable AI?",
    ]
    
    print("\n" + "="*80)
    print("RUNNING FULL RAG PIPELINE INTEGRATION TESTS")
    print("="*80)
    
    results = []
    for query in test_queries:
        passed = test_query(query)
        results.append((query, passed))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for query, p in results:
        status = "✅ PASS" if p else "❌ FAIL"
        print(f"{status}: {query[:60]}...")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
