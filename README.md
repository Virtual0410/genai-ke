# GenAI Knowledge Engine

An end-to-end document processing pipeline designed for Retrieval-Augmented Generation (RAG) systems.

This project incrementally builds the core components required for a production-grade GenAI system,
starting from raw document ingestion to clean, retrievable knowledge units.

---

## Architecture Overview

Raw PDFs
  ↓
Page-Level Ingestion
  ↓
Text Cleaning & Normalization
  ↓
Semantic Chunking
  ↓
(Embeddings & Retrieval — upcoming)

---

## Module 1: Document Ingestion

- Ingests PDF documents page-by-page
- Preserves source file and page numbers
- Enables traceability and grounded citations

**Why page-level ingestion?**
Page-level granularity allows precise retrieval, debugging, and hallucination analysis
by tracing generated answers back to their original source.

---

## Module 2: Text Cleaning & Normalization

- Removes repeated headers, footers, and page numbers
- Normalizes whitespace and broken line structures
- Preserves original document metadata

**Design principle:**  
Cleaning is deliberately separated from loading to ensure reproducibility,
debuggability, and iterative improvement without re-ingesting raw documents.

---

## Module 3: Chunking Strategy

Two chunking approaches are implemented:

### Fixed-Size Chunking
- Splits text into overlapping fixed-length segments
- Used as a baseline for comparison

### Semantic Chunking
- Splits text along natural paragraph and section boundaries
- Preserves semantic coherence and improves retrieval precision

Each chunk retains metadata (source, page, position) to support
citations, trust, and system observability.

---

## Project Philosophy

- Prioritizes data quality over prompt engineering
- Treats hallucinations as retrieval and data issues
- Emphasizes traceability and explainability

---

## Status

- [x] PDF Ingestion
- [x] Text Cleaning
- [x] Chunking
- [ ] Embeddings & Vector Indexing
- [ ] Retrieval & RAG
- [ ] Evaluation & Hallucination Analysis
- [ ] Deployment

