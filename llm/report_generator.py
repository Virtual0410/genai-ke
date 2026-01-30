def generate_research_report(query, stance_groups, gap_insights, selected_chunks):
    report = []

    report.append(f"Research Summary for Query: {query}\n")

    total_sources = len(selected_chunks)
    report.append(f"Total sources consulted: {total_sources}")

    # Stance overview
    report.append("\nEvidence Perspective:")
    for stance, items in stance_groups.items():
        report.append(f"- {stance}: {len(items)} sources")

    # Gap insights
    if gap_insights:
        report.append("\nResearch Gaps Identified:")
        for g in gap_insights:
            report.append(f"- {g}")

    # Source listing
    report.append("\nKey Sources:")
    for c in selected_chunks:
        data = c["data"]
        report.append(f"- {data['source']} (page {data['page']})")

    return "\n".join(report)
