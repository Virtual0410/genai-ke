"""
Generic reranking based on chunk quality signals.
Removed query-specific hacks.
"""
from config import get_config

def rerank(results, query=None):
    """
    Rerank results based on chunk quality metrics.
    
    Quality signals:
    - Chunk length (penalize too short/long)
    - Score from retrieval
    
    No query-specific hacks - relies on semantic similarity.
    """
    min_len = get_config("reranking.min_chunk_length", 100)
    max_len = get_config("reranking.max_chunk_length", 1000)
    short_penalty = get_config("reranking.short_chunk_penalty", 0.5)
    long_penalty = get_config("reranking.long_chunk_penalty", 0.8)
    
    reranked = []
    
    for r in results:
        text = r["data"]["text"]
        score = r.get("score", 0.5)
        length = len(text)
        
        # Length-based quality adjustments
        if length < min_len:
            score *= short_penalty
        elif length > max_len:
            score *= long_penalty
        
        reranked.append({
            "score": score,
            "data": r["data"]
        })
    
    # Sort by adjusted score
    reranked.sort(key=lambda x: x["score"], reverse=True)
    
    return reranked
