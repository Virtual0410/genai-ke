# GenAI Knowledge Engine

## Module 1: Data Ingestion (PDF)

This module ingests raw PDF documents and converts them into
page-aware structured text units for downstream RAG pipelines.

### Why page-level ingestion?
Each page is stored independently to:
- enable grounded citations
- improve traceability
- reduce hallucinations during generation
