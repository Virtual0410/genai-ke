from typing import List


def fixed_size_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into fixed-size overlapping chunks.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


def semantic_chunk(text: str) -> List[str]:
    """
    Split text using paragraph boundaries.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs
