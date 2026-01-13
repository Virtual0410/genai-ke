# Retrieval top_k Analysis

## Experiment Setup
- Query: "Explain the evolution of machine learning"
- Embedding model: all-mpnet-base-v2
- Score threshold: 0.3
- Tested top_k values: 3, 5, 8

## Observations

### top_k = 3
- Retrieved only the most relevant chunks
- Excluded weaker contextual sections (e.g., Future Trends)
- Produced the cleanest and most focused result set
- Best suited for QA-style retrieval

### top_k = 5
- Included additional contextual information
- Added semantically related but less relevant sections
- Balanced relevance and context

### top_k = 8
- Retrieved the same set as top_k = 5 due to score threshold filtering
- Demonstrated that score_threshold effectively limits noise
- No degradation in ranking order

## Cross-Run Insights
- Ranking order remained stable across all top_k values
- Score threshold played a stronger role than top_k in final result count
- Retriever behavior was deterministic and predictable

## Conclusion
- top_k controls candidate breadth, not final result count
- score_threshold is the primary noise control mechanism
- top_k = 3 is optimal for focused QA retrieval
- top_k = 4–5 is suitable for contextual or exploratory queries
