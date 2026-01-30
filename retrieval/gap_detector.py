def detect_research_gaps(grouped_docs, stance_groups):
    insights = []

    total_docs = len(grouped_docs)

    if total_docs <= 1:
        insights.append("Limited number of sources discuss this topic.")

    if stance_groups["support"] == [] and stance_groups["question"] == []:
        insights.append("No strong evaluative perspectives found in sources.")

    if len(grouped_docs) < 2:
        insights.append("Insufficient cross-document comparison possible.")

    return insights
