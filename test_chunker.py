from ingestion.pdf_loader import load_pdf
from ingestion.cleaner import clean_document
from ingestion.chunker import semantic_chunk
import json

docs = load_pdf("data/raw/sample.pdf")
cleaned_docs = [clean_document(doc) for doc in docs]

all_chunks = []

for doc in cleaned_docs:
    chunks = semantic_chunk(doc["text"])

    for i, chunk in enumerate(chunks):
        all_chunks.append({
            "chunk_id": f"{doc['source']}_p{doc['page']}_c{i}",
            "text": chunk,
            "source": doc["source"],
            "page": doc["page"]
        })

with open("data/processed/sample_chunks.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2, ensure_ascii=False)

print(f"Generated {len(all_chunks)} chunks")
print("First chunk:")
print(all_chunks[0])
