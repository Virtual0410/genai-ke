from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore


class Retriever:
    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        top_k: int = 4,
        score_threshold: float = 0.35
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = top_k
        self.score_threshold = score_threshold

    def retrieve(self, query: str):
        query_embedding = self.embedder.embed_texts([query])
        results = self.vector_store.search(query_embedding, self.top_k)

        filtered = [
            r for r in results
            if r["score"] >= self.score_threshold
        ]

        return filtered
