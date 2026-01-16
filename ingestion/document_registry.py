import hashlib
from pathlib import Path

def generate_doc_id(file_path: str) -> str:
    """
    Generate a deterministic document ID.
    Same file path → same ID every time.
    """
    return "doc_" + hashlib.md5(file_path.encode()).hexdigest()[:8]

def register_document(file_path: str, doc_type: str, published_date: str):
    """
    Register document metadata.
    """
    return {
        "doc_id": generate_doc_id(file_path),
        "doc_name": Path(file_path).name,
        "doc_type": doc_type,
        "published_date": published_date,
        "path": file_path
    }
