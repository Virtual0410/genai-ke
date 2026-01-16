def load_text(file_path: str):
    """
    Load text or markdown files.
    Returns a list with a single 'page' for consistency.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return [text]
