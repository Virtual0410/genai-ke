"""
Context selection based on document authority.
"""
from config import get_config

def select_context(grouped_results, doc_authority):
    """
    Select context chunks based on document authority.
    Uses configurable limits for max documents and chunks.
    """
    max_docs = get_config("context_selection.max_docs", 3)
    max_chunks_per_doc = get_config("context_selection.max_chunks_per_doc", 4)
    min_authority = get_config("context_selection.min_authority_score", 0.3)
    
    # Rank documents by authority
    ranked_docs = sorted(
        doc_authority.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Filter by minimum authority threshold
    ranked_docs = [
        (doc_id, score) for doc_id, score in ranked_docs
        if score >= min_authority
    ]
    
    selected_chunks = []
    
    for doc_id, authority in ranked_docs[:max_docs]:
        chunks = grouped_results.get(doc_id, [])
        
        # Sort chunks by relevance score
        chunks = sorted(chunks, key=lambda r: r["score"], reverse=True)
        
        # Take top chunks from this document
        selected_chunks.extend(chunks[:max_chunks_per_doc])
    
    return selected_chunks
