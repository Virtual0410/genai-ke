"""
Proper BM25 keyword retrieval implementation.
Replaces naive string matching.
"""
import math
from collections import Counter
from typing import List, Dict
from config import get_config

class BM25Retriever:
    """
    BM25 (Best Matching 25) ranking function.
    Proper term frequency / inverse document frequency scoring.
    """
    
    def __init__(self, documents: List[Dict], k1=1.5, b=0.75):
        """
        Args:
            documents: List of document metadata dicts with 'text' field
            k1: Term frequency saturation parameter (default 1.5)
            b: Length normalization parameter (default 0.75)
        """
        self.documents = documents
        self.k1 = k1
        self.b = b
        
        # Tokenize all documents
        self.tokenized_docs = [self._tokenize(doc["text"]) for doc in documents]
        
        # Calculate document frequencies
        self.doc_freqs = self._calculate_doc_frequencies()
        
        # Calculate average document length
        self.avg_doc_len = sum(len(doc) for doc in self.tokenized_docs) / len(self.tokenized_docs)
        
        # Number of documents
        self.num_docs = len(documents)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization - split on whitespace and lowercase."""
        return text.lower().split()
    
    def _calculate_doc_frequencies(self) -> Dict[str, int]:
        """Calculate how many documents contain each term."""
        doc_freqs = {}
        for doc in self.tokenized_docs:
            unique_terms = set(doc)
            for term in unique_terms:
                doc_freqs[term] = doc_freqs.get(term, 0) + 1
        return doc_freqs
    
    def _idf(self, term: str) -> float:
        """Calculate IDF (Inverse Document Frequency) for a term."""
        df = self.doc_freqs.get(term, 0)
        if df == 0:
            return 0.0
        # IDF formula: log((N - df + 0.5) / (df + 0.5) + 1)
        return math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1.0)
    
    def _bm25_score(self, query_terms: List[str], doc_idx: int) -> float:
        """Calculate BM25 score for a document given query terms."""
        doc = self.tokenized_docs[doc_idx]
        doc_len = len(doc)
        
        # Term frequencies in document
        term_freqs = Counter(doc)
        
        score = 0.0
        for term in query_terms:
            if term not in term_freqs:
                continue
            
            tf = term_freqs[term]
            idf = self._idf(term)
            
            # BM25 formula
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
            
            score += idf * (numerator / denominator)
        
        return score
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve top-k documents for a query using BM25 scoring.
        
        Returns:
            List of dicts with 'score' and original document metadata
        """
        if top_k is None:
            top_k = get_config("retrieval.keyword_top_k", 5)
        
        query_terms = self._tokenize(query)
        
        # Score all documents
        scores = []
        for idx in range(len(self.documents)):
            score = self._bm25_score(query_terms, idx)
            if score > 0:  # Only include docs with non-zero scores
                scores.append({
                    "score": score,
                    "chunk_id": self.documents[idx].get("chunk_id", f"doc_{idx}"),
                    **self.documents[idx]  # Include all original metadata
                })
        
        # Sort by score descending
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        return scores[:top_k]


class KeywordRetriever:
    """
    Wrapper maintaining old interface but using BM25 internally.
    """
    
    def __init__(self, metadata: List[Dict]):
        self.bm25 = BM25Retriever(metadata)
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict]:
        """Retrieve using BM25 (backward compatible interface)."""
        return self.bm25.retrieve(query, top_k)
