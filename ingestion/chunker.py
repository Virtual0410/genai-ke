"""
Text chunking strategies for document processing.
"""
from typing import List
from config import get_config

def chunk_text(text: str, strategy: str = None) -> List[str]:
    """
    Chunk text using specified strategy.
    
    Args:
        text: Input text to chunk
        strategy: 'semantic' or 'fixed_size' (reads from config if None)
    
    Returns:
        List of text chunks
    """
    if strategy is None:
        strategy = get_config("chunking.strategy", "semantic")
    
    if strategy == "semantic":
        return semantic_chunk(text)
    elif strategy == "fixed_size":
        chunk_size = get_config("chunking.fixed_size_chars", 500)
        overlap = get_config("chunking.fixed_size_overlap", 50)
        return fixed_size_chunk(text, chunk_size, overlap)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")

def fixed_size_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into fixed-size overlapping chunks.
    Tries to break at sentence boundaries when possible.
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # If not at end, try to break at sentence boundary
        if end < text_length:
            # Look for sentence endings near the chunk boundary
            search_start = max(start, end - 100)
            search_text = text[search_start:end + 50]
            
            # Find last sentence ending
            for delimiter in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
                last_pos = search_text.rfind(delimiter)
                if last_pos != -1:
                    end = search_start + last_pos + len(delimiter)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < text_length else text_length
    
    return chunks

def semantic_chunk(text: str) -> List[str]:
    """
    Split text at natural boundaries (paragraphs and sections).
    Preserves semantic coherence better than fixed-size chunking.
    """
    min_length = get_config("chunking.semantic_min_length", 50)
    
    # First try to split on double newlines (paragraphs)
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        para_length = len(para)
        
        # If single paragraph is too long, split it further
        if para_length > 1000:
            # Try splitting on single newlines
            subparas = para.split('\n')
            for subpara in subparas:
                subpara = subpara.strip()
                if subpara:
                    chunks.append(subpara)
        elif current_length + para_length > 800:
            # Current chunk is getting too big, start new one
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_length = para_length
        else:
            # Add to current chunk
            current_chunk.append(para)
            current_length += para_length
    
    # Add final chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    # Filter out chunks that are too short
    chunks = [c for c in chunks if len(c) >= min_length]
    
    return chunks if chunks else [text]
