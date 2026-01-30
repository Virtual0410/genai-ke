def group_chunks_by_source(chunks):
    grouped = {}

    for r in chunks:
        doc_id = r["data"]["doc_id"]
        grouped.setdefault(doc_id, []).append(r)

    return grouped

def build_synthesis_context(grouped_chunks):
    context_blocks = []

    for doc_id, chunk_list in grouped_chunks.items():
        block = "\n".join(
            c["data"]["text"].strip()
            for c in chunk_list[:2]
        )
        context_blocks.append(block)

    return "\n\n".join(context_blocks)
