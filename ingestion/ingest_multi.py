from ingestion.document_registry import register_document
from ingestion.pdf_loader import load_pdf
from ingestion.text_loader import load_text
from ingestion.chunker import fixed_size_chunk
import json

DOCUMENTS = [
    {
        "path": "data/raw/research/ml_research_paper1.pdf",
        "doc_type": "research_paper",
        "published_date": "2024-01-01"
    },
    {
        "path": "data/raw/research/ml_research_paper2.pdf",
        "doc_type": "research_paper",
        "published_date": "2024-01-02"
    },
    {
        "path": "data/raw/research/ml_research_paper3.pdf",
        "doc_type": "research_paper",
        "published_date": "2024-03-12"
    },
    {
        "path": "data/raw/blogs/ai_healthcare_blog.md",
        "doc_type": "blog",
        "published_date": "2025-07-07"
    },
    {
        "path": "data/raw/notes/ml_notes.txt",
        "doc_type": "notes",
        "published_date": "2025-11-22"
    }
]

all_documents = []

for doc in DOCUMENTS:

    meta = register_document(
        file_path=doc["path"],
        doc_type=doc["doc_type"],
        published_date=doc["published_date"]
    )

    if doc["path"].endswith(".pdf"):
        pages = load_pdf(doc["path"])
    else:
        pages = load_text(doc["path"])

    all_documents.append({
        "meta": meta,
        "pages": pages
    })

all_chunks = []

for doc in all_documents:
    meta = doc["meta"]

    for page_num, page in enumerate(doc["pages"], start=1):

    # Extract raw text correctly
        if isinstance(page, dict):
            page_text = page.get("text", "")
        else:
            page_text = page

        text_chunks = fixed_size_chunk(page_text)

        for i, chunk_text in enumerate(text_chunks):
            all_chunks.append({
                "chunk_id": f"{meta['doc_id']}_chunk_{page_num}_{i}",
                "doc_id": meta["doc_id"],
                "doc_name": meta["doc_name"],
                "doc_type": meta["doc_type"],
                "published_date": meta["published_date"],
                "source": meta["doc_name"],
                "page": page_num,
                "text": chunk_text
            })

with open("data/processed/sample_chunks_multi.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2)
