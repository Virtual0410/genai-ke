"""
Improved coherence filter with stopword handling.
"""
from config import get_config

# Common English stopwords
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'what', 'when', 'where', 'who', 'how'
}

def filter_by_topic_coherence(query, chunks):
    """
    Filter chunks by semantic relevance to query.
    Now properly handles stopwords and uses config.
    """
    if not get_config("coherence.enabled", False):
        # Coherence filter disabled - return all chunks
        return chunks
    
    # Extract meaningful query terms (remove stopwords)
    query_lower = query.lower()
    query_terms = query_lower.split()
    
    if get_config("coherence.use_stopwords", True):
        query_terms = [term for term in query_terms if term not in STOPWORDS]
    
    # If no meaningful terms left, return all chunks
    if not query_terms:
        return chunks
    
    query_terms_set = set(query_terms)
    min_overlap = get_config("coherence.min_term_overlap", 2)
    
    filtered = []
    
    for chunk in chunks:
        text = chunk["data"]["text"].lower()
        
        # Count overlapping meaningful terms
        overlap = sum(1 for term in query_terms_set if term in text)
        
        # Keep chunk if it has enough meaningful term overlap
        if overlap >= min(min_overlap, len(query_terms_set)):
            filtered.append(chunk)
    
    # If filter is too aggressive, return original chunks
    if len(filtered) < 2 and len(chunks) > 2:
        return chunks
    
    return filtered if filtered else chunks
