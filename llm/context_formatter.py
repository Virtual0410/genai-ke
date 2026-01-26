def format_context(chunks):
    """
    Format retrieved chunks into citation-ready context.
    """
    formatted = []

    for i, r in enumerate(chunks, start=1):
        d = r["data"]
        formatted.append(
            f"[{i}] {d['text'].strip()}\n"
            f"    (Source: {d['doc_name']}, page {d['page']})"
        )

    return "\n\n".join(formatted)
