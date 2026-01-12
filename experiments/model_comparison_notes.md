# Embedding Model Comparison Notes

## Models Tested
- all-MiniLM-L6-v2
- all-mpnet-base-v2
- multi-qa-MiniLM-L6-cos-v1

## Observations

### all-MiniLM-L6-v2
- Fast and stable baseline model
- Retrieves generally relevant content but shows weak intent discrimination
- Sensitive to chunk noise and multi-topic chunks
- Suitable for quick semantic search but suboptimal for QA-focused RAG

### all-mpnet-base-v2
- Strongest semantic understanding and score separation
- Best performance on explanatory and historical queries
- More resistant to noisy metadata
- Retrieval quality limited primarily by chunk structure, not model capacity
- Best general-purpose embedding model tested

### multi-qa-MiniLM-L6-cos-v1
- Best alignment for direct question-answer queries
- Correctly prioritizes answer-like sections (e.g., applications, future trends)
- Less reliable for narrative or descriptive queries
- Most suitable for RAG-style QA systems

## Cross-Model Insights
- Model choice significantly impacts ranking order and similarity scores
- Chunk quality is currently the primary bottleneck across all models
- All models correctly reject out-of-scope queries (e.g., "What is API?"), indicating grounded retrieval

## Conclusion
- all-mpnet-base-v2 is the best overall semantic retriever
- multi-qa-MiniLM-L6-cos-v1 is preferred for QA-driven RAG
- Improving chunking strategy will yield larger gains than further model changes
