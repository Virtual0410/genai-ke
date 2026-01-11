import re
from typing import Dict


def clean_text(text: str) -> str:
    """
    Cleans raw extracted PDF text and returns normalized text.
    """

    # 1. Replace multiple spaces and newlines with a single space
    text = re.sub(r"\s+", " ", text)

    # 2. Remove common page number patterns like "Page 12"
    text = re.sub(r"Page\s+\d+", "", text, flags=re.IGNORECASE)

    # 3. Strip leading and trailing whitespace
    text = text.strip()

    return text


def clean_document(doc: Dict) -> Dict:
    """
    Cleans a single page document while preserving metadata.
    """

    cleaned_text = clean_text(doc["text"])

    return {
        "text": cleaned_text,
        "source": doc["source"],
        "page": doc["page"]
    }
