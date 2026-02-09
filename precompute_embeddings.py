"""
Pre-compute embeddings for all documents and save to disk.
Run this once after ingesting new documents.
"""
import json
import pickle
from pathlib import Path
import numpy as np
from embeddings.embedder import Embedder

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
CACHE_DIR = PROJECT_ROOT / "cache"

def precompute_embeddings(
    input_file="sample_chunks_multi.json",
    model_name="all-MiniLM-L6-v2"
):
    """
    Pre-compute embeddings and save to cache directory.
    """
    CACHE_DIR.mkdir(exist_ok=True)
    
    input_path = DATA_DIR / input_file
    print(f"Loading chunks from: {input_path}")
    
    with open(input_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    texts = [c["text"] for c in chunks]
    
    print(f"Computing embeddings for {len(texts)} chunks using {model_name}...")
    embedder = Embedder(model_name)
    embeddings = embedder.embed_texts(texts)
    
    # Save embeddings
    embeddings_path = CACHE_DIR / f"embeddings_{model_name.replace('/', '_')}.npy"
    np.save(embeddings_path, embeddings)
    print(f"Saved embeddings to: {embeddings_path}")
    
    # Save metadata
    metadata_path = CACHE_DIR / f"metadata_{model_name.replace('/', '_')}.pkl"
    with open(metadata_path, "wb") as f:
        pickle.dump(chunks, f)
    print(f"Saved metadata to: {metadata_path}")
    
    # Save embedding dimension
    config_path = CACHE_DIR / f"embedding_config_{model_name.replace('/', '_')}.json"
    with open(config_path, "w") as f:
        json.dump({
            "model_name": model_name,
            "embedding_dim": embeddings.shape[1],
            "num_chunks": len(chunks)
        }, f, indent=2)
    print(f"Saved config to: {config_path}")
    
    print(f"\n[SUCCESS] Pre-computed embeddings complete!")
    print(f"   - {len(chunks)} chunks")
    print(f"   - Embedding dimension: {embeddings.shape[1]}")
    print(f"   - Model: {model_name}")

if __name__ == "__main__":
    precompute_embeddings()
