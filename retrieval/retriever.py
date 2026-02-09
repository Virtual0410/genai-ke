"""
Semantic retriever using embeddings.
"""
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore


class Retriever:
    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        top_k: int = 10,  # Increased from 4 to get more candidates
        score_threshold: float = 0.3  # Lowered from 0.35 to be less restrictive
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = top_k
        self.score_threshold = score_threshold

    def retrieve(self, query: str, top_k: int = None):
        """
        Retrieve semantically similar chunks.
        
        Args:
            query: Search query
            top_k: Number of results (uses default if None)
        
        Returns:
            List of results with scores above threshold
        """
        # Use provided top_k or fall back to default
        k = top_k if top_k is not None else self.top_k
        
        query_embedding = self.embedder.embed_texts([query])
        results = self.vector_store.search(query_embedding, k)

        # Filter by score threshold
        filtered = [
            r for r in results
            if r["score"] >= self.score_threshold
        ]

        return filtered
