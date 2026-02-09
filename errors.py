"""
Error types for RAG system.
"""

class RAGError(Exception):
    """Base exception for RAG system errors."""
    pass

class DataLoadError(RAGError):
    """Error loading data files."""
    pass

class EmbeddingError(RAGError):
    """Error during embedding computation or loading."""
    pass

class RetrievalError(RAGError):
    """Error during retrieval process."""
    pass

class LLMError(RAGError):
    """Error during LLM generation."""
    pass

class ConfigError(RAGError):
    """Error in configuration."""
    pass
