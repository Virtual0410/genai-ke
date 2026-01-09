from ingestion.pdf_loader import load_pdf, save_documents

pdf_path = "data/raw/sample.pdf"
output_path = "data/processed/sample.json"

docs = load_pdf(pdf_path)

print(f"Extracted {len(docs)} pages")

if docs:
    print("First page sample:")
    print(docs[0])

save_documents(docs, output_path)
