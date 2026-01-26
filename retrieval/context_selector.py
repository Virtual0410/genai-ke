def select_context(
    grouped_results,
    doc_authority,
    max_docs=2,
    max_chunks_per_doc=3
):
    """
    Select context chunks based on document authority.
    """

    # Rank documents by authority
    ranked_docs = sorted(
        doc_authority.items(),
        key=lambda x: x[1],
        reverse=True
    )

    selected_chunks = []

    for doc_id, _ in ranked_docs[:max_docs]:
        chunks = grouped_results.get(doc_id, [])
        chunks = sorted(chunks, key=lambda r: r["score"], reverse=True)

        selected_chunks.extend(chunks[:max_chunks_per_doc])

    return selected_chunks
