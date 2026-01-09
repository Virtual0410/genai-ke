import pdfplumber
from pathlib import Path
import json


def load_pdf(pdf_path: str):
    pdf_path = Path(pdf_path)
    documents = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()

            if text and text.strip():
                documents.append({
                    "text": text,
                    "source": pdf_path.name,
                    "page": page_number
                })

    return documents


def save_documents(documents, output_path: str):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
