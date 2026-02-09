"""
Quick diagnostic test for the RAG pipeline.
"""
from pipeline.run_query import run_query, clear_cache

# Clear any cached state
clear_cache()

# Test query
query = "How is explainable AI evaluated across research papers?"

print(f"Testing query: {query}\n")
print("=" * 60)

try:
    result = run_query(query)
    
    print("\n[SUCCESS] Query executed successfully!\n")
    print(f"Answer: {result['answer'][:200]}...")
    print(f"\nSources: {len(result['sources'])} documents cited")
    print(f"Stance groups: {list(result['stance'].keys())}")
    
    if result.get('error'):
        print(f"\n[WARNING] {result['error']}")
    
except Exception as e:
    print(f"\n[ERROR] Query failed with error:")
    print(f"  {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
