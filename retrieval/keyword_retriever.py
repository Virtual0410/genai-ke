from collections import Counter


class KeywordRetriever:
    def __init__(self, documents):
        self.documents = documents
        self.doc_tokens = [
            Counter(doc["text"].lower().split())
            for doc in documents
        ]

    def score(self, query, doc_idx):
        query_tokens = query.lower().split()
        score = 0
        for token in query_tokens:
            score += self.doc_tokens[doc_idx].get(token, 0)
        return score

    def retrieve(self, query, top_k=5):
        scored = [
            (i, self.score(query, i))
            for i in range(len(self.documents))
        ]

        scored.sort(key=lambda x: x[1], reverse=True)

        return [
            self.documents[i]
            for i, score in scored[:top_k]
            if score > 0
        ]
