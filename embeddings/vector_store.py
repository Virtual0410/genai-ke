import faiss
import numpy as np


class VectorStore:
    def __init__(self, embedding_dim: int):
        self.index = faiss.IndexFlatIP(embedding_dim)
        self.metadata = []

    def add(self, embeddings, metadatas):
        # Convert to numpy float32
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings)

        embeddings = embeddings.astype("float32")

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)
        self.metadata.extend(metadatas)

    def search(self, query_embedding, top_k=5):
        # Convert to numpy float32
        if not isinstance(query_embedding, np.ndarray):
            query_embedding = np.array(query_embedding)

        query_embedding = query_embedding.astype("float32")

        # Ensure shape (1, D)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Normalize query
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append({
                "score": float(score),
                "data": self.metadata[idx]
            })

        return results
