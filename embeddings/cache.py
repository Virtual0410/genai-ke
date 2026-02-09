"""
Embedding cache manager for pre-computed embeddings.
Solves the performance issue of re-embedding on every query.
"""
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from embeddings.embedder import Embedder
from config_loader import get_config


class EmbeddingCache:
    """Manages persistent embedding cache"""
    
    def __init__(self, cache_path: str = None):
        if cache_path is None:
            cache_path = get_config('embeddings', 'cache_path', default='data/cache/embeddings.pkl')
        
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save(self, embeddings: np.ndarray, metadata: List[Dict], chunks: List[Dict]):
        """Save embeddings, metadata, and original chunks to cache"""
        cache_data = {
            'embeddings': embeddings,
            'metadata': metadata,
            'chunks': chunks,
            'model_name': get_config('embeddings', 'model_name'),
            'embedding_dim': embeddings.shape[1]
        }
        
        with open(self.cache_path, 'wb') as f:
            pickle.dump(cache_data, f)
        
        print(f"[OK] Embeddings cached to {self.cache_path}")
    
    def load(self) -> Tuple[np.ndarray, List[Dict], List[Dict]]:
        """Load embeddings, metadata, and chunks from cache"""
        if not self.cache_path.exists():
            raise FileNotFoundError(f"Cache not found: {self.cache_path}")
        
        with open(self.cache_path, 'rb') as f:
            cache_data = pickle.load(f)
        
        # Validate model consistency
        cached_model = cache_data.get('model_name')
        current_model = get_config('embeddings', 'model_name')
        
        if cached_model != current_model:
            raise ValueError(
                f"Model mismatch: cache uses '{cached_model}', "
                f"config specifies '{current_model}'"
            )
        
        print(f"[OK] Loaded embeddings from cache ({cache_data['embeddings'].shape[0]} chunks)")
        
        return (
            cache_data['embeddings'],
            cache_data['metadata'],
            cache_data['chunks']
        )
    
    def exists(self) -> bool:
        """Check if cache exists"""
        return self.cache_path.exists()
    
    def clear(self):
        """Delete cache file"""
        if self.cache_path.exists():
            self.cache_path.unlink()
            print(f"[OK] Cache cleared: {self.cache_path}")


def build_embeddings_cache(chunks_file: str = None, force_rebuild: bool = False):
    """
    Build or rebuild embedding cache from chunks file.
    Call this once after ingestion or when chunks change.
    """
    if chunks_file is None:
        chunks_file = get_config('paths', 'chunks_file')
    
    cache = EmbeddingCache()
    
    # Check if cache exists and we're not forcing rebuild
    if cache.exists() and not force_rebuild:
        print(f"[WARNING] Cache already exists. Use force_rebuild=True to regenerate.")
        return
    
    print("[BUILDING] Building embedding cache...")
    
    # Load chunks
    import json
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Extract texts and metadata
    texts = [c['text'] for c in chunks]
    metadata = [{k: v for k, v in c.items()} for c in chunks]
    
    # Generate embeddings
    model_name = get_config('embeddings', 'model_name')
    embedder = Embedder(model_name)
    embeddings = embedder.embed_texts(texts)
    
    # Save to cache
    cache.save(embeddings, metadata, chunks)
    
    print(f"[OK] Cache built successfully: {len(chunks)} chunks embedded")


if __name__ == "__main__":
    # CLI tool to build cache
    import sys
    
    force = '--force' in sys.argv or '-f' in sys.argv
    
    try:
        build_embeddings_cache(force_rebuild=force)
    except Exception as e:
        print(f"Error building cache: {e}")
        sys.exit(1)
