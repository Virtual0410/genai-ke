# GenAI Knowledge Engine

A fully local, end-to-end Retrieval-Augmented Generation (RAG) system
built from first principles, focusing on data quality, semantic retrieval,
traceability, and hallucination control.

This project incrementally constructs the core components of a
production-grade GenAI system instead of relying on black-box APIs.

---

## Architecture Overview

Raw Documents (PDFs)<br>
  ↓<br>
Page-Level Ingestion<br>
  ↓<br>
Text Cleaning & Normalization<br>
  ↓<br>
Semantic Chunking<br>
  ↓<br>
Embeddings & Vector Search<br>
  ↓<br>
Retriever (Top-K Context)<br>
  ↓<br>
Local LLM (RAG Answer Generation)

---

**Note:** Small processed data samples are included under `data/processed/` to make the pipeline reproducible and easier to review.

## Module 1: Document Ingestion

- Ingests PDF documents page-by-page
- Preserves source filename and page numbers
- Enables precise traceability and grounded citations

**Why page-level ingestion?**  
Page-level granularity allows debugging hallucinations and tracing
generated answers back to their original source.

---

## Module 2: Text Cleaning & Normalization

- Removes repeated headers, footers, and page numbers
- Normalizes whitespace and broken line structures
- Preserves original metadata for auditability

**Design principle:**  
Cleaning is intentionally separated from loading to allow reproducibility
and iterative improvement without re-ingesting raw documents.

---

## Module 3: Chunking Strategy

Text is split into retrievable knowledge units using two approaches:

### Fixed-Size Chunking
- Splits text into overlapping fixed-length chunks
- Used as a baseline for comparison

### Semantic Chunking
- Splits text along natural paragraph boundaries
- Preserves semantic coherence
- Improves retrieval precision and reduces noise

Each chunk retains metadata (source, page, chunk ID) to support
citations and debugging.

---

## Module 4: Embeddings & Vector Search (Day 4)

This module converts text chunks into semantic embeddings and indexes
them using a local vector database for meaning-based retrieval.

### Embedding Generation
- Uses SentenceTransformers to generate normalized embeddings
- Multiple embedding models evaluated:
  - all-MiniLM-L6-v2
  - all-mpnet-base-v2
  - multi-qa-MiniLM-L6-cos-v1
- Embeddings are normalized to enable cosine similarity search

### Evaluation Scripts

All embedding evaluations and comparisons are implemented as standalone scripts
under the `experiments/` directory, including:
- Multi-model embedding comparison
- Similarity score inspection
- Confidence-based “no answer” detection
- Retrieval failure case analysis

### Vector Indexing
- FAISS (IndexFlatIP) used for exact similarity search
- Stores embeddings locally with associated chunk metadata
- Enables fast Top-K semantic retrieval

### Model Evaluation & Comparison
- Multiple embedding models compared using the same document corpus
- Real document-based queries used for evaluation
- Similarity scores inspected to analyze ranking behavior
- Failure cases documented where retrieval was weak or ambiguous
- Detailed observations recorded in model comparison notes

**Key insight:**  
Most hallucinations originate from poor retrieval quality rather than
LLM behavior. Improving embeddings and chunking directly improves
answer reliability.

---

## Project Philosophy

- Data quality > prompt engineering
- Retrieval quality > model size
- Traceability and explainability are first-class concerns
- LLMs are treated as interchangeable generation layers

---

## Current Status

- [x] PDF Ingestion
- [x] Text Cleaning & Normalization
- [x] Semantic Chunking
- [x] Embeddings & Vector Search (FAISS)
- [ ] Retrieval Engineering (Hybrid Search & Ranking)
- [ ] Local LLM Integration (RAG)
- [ ] Evaluation & Hallucination Control
- [ ] Deployment

