from ingestion.pdf_loader import load_pdf, save_documents
from ingestion.cleaner import clean_document

# Load raw PDF pages
docs = load_pdf("data/raw/sample.pdf")

# Clean each page
cleaned_docs = [clean_document(doc) for doc in docs]

# Save cleaned output
save_documents(cleaned_docs, "data/processed/sample_cleaned.json")

print(f"Cleaned {len(cleaned_docs)} pages")
print("Sample cleaned page:")
print(cleaned_docs[0])
