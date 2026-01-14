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
Embeddings & Vector Search (FAISS)<br>
↓<br>
Hybrid Retrieval (Semantic + Keyword)<br>
↓<br>
Reranking & Confidence Gate<br>
↓<br>
Local LLM (Ollama) — Grounded Answer / Refusal

---

**Note:** Small processed data samples are included under `data/processed/`
to keep the pipeline reproducible and easy to review.

---

## Module 1: Document Ingestion

- Ingests PDF documents page-by-page
- Preserves source filename and page numbers
- Produces a consistent internal document schema

**Why page-level ingestion?**  
Page-level granularity enables precise citation, debugging of retrieval
failures, and traceability of generated answers back to original sources.

---

## Module 2: Text Cleaning & Normalization

- Removes repeated headers, footers, and page artifacts
- Normalizes whitespace and broken line structures
- Preserves semantic meaning and metadata
- Outputs cleaned, audit-friendly documents

**Design principle:**  
Cleaning is isolated from ingestion to allow iterative improvement
without reprocessing raw data.

---

## Module 3: Chunking Strategy

Text is split into retrievable knowledge units using structure-aware logic.

### Semantic Chunking
- Splits text along natural paragraph and section boundaries
- Preserves semantic coherence
- Reduces embedding dilution and retrieval noise

Each chunk retains:
- `chunk_id`
- source document
- page number

This enables precise citations and debugging.

**Key insight:**  
Chunking is a retrieval decision, not a preprocessing afterthought.

---

## Module 4: Embeddings & Vector Search

This module converts text chunks into semantic embeddings and indexes
them for similarity-based retrieval.

### Embedding Generation
- Uses SentenceTransformers for local embedding generation
- Multiple models evaluated:
  - `all-MiniLM-L6-v2`
  - `all-mpnet-base-v2`
  - `multi-qa-MiniLM-L6-cos-v1`
- Final model selected based on ranking stability and score separation

### Vector Indexing
- FAISS (`IndexFlatIP`) used for cosine similarity search
- Stores embeddings locally with associated metadata
- Enables fast and deterministic Top-K retrieval

### Evaluation & Analysis
- Multi-model comparisons performed on real document queries
- Similarity score distributions inspected
- Failure cases documented
- Final model choice justified with evidence

**Key insight:**  
Embeddings determine *what can be retrieved*, not *what is correct*.

---

## Module 5: Retrieval Engineering

This module implements a **production-grade retrieval layer** responsible
for deciding *what context is allowed to reach the LLM*.

Instead of relying on raw vector search, the system applies multiple
retrieval signals, reranking logic, and confidence checks.

---

### Retrieval Pipeline

User Query<br>
→ Query Embedding<br>
→ Semantic Retrieval (FAISS)<br>
→ Keyword Retrieval (BM25-lite)<br>
→ Merge & Deduplicate<br>
→ Reranking (Intent-aware)<br>
→ Confidence Gate<br>
→ Final Context **or** Refusal

---

### Semantic Retrieval

- Retrieves top-K semantically similar chunks using FAISS
- Applies similarity score thresholding
- Filters weak or ambiguous matches early

---

### Keyword-Based Retrieval (BM25-lite)

- Token-based exact matching
- Complements semantic retrieval where embeddings fail
- Useful for acronyms, section titles, and technical terms

---

### Hybrid Retrieval Strategy

- Semantic and keyword results are:
  - normalized into a unified `{score, data}` format
  - merged and deduplicated by `chunk_id`
- Ensures consistent downstream behavior

---

### Reranking Logic (Intent-Aware)

Retrieved chunks are reranked using heuristic rules:
- Penalize very short or overly long chunks
- Prefer mid-length, information-dense chunks
- Boost sections matching query intent (e.g., “future”, “trends”)
- Penalize abstracts and introductions for specific queries

This prioritizes *answer-bearing context* over generic text.

---

### Confidence & Hallucination Control

Before generation, the system checks:
- Whether sufficient high-quality context exists
- Whether similarity scores exceed minimum thresholds

If context quality is insufficient, the system **refuses to answer**
instead of hallucinating.

> “I don’t know” is treated as a feature, not a failure.

**Key insight:**  
Most hallucinations are retrieval failures, not model failures.

---

## Module 6: Local LLM Integration (Responsible RAG)

- Integrated a local LLM using **Ollama**
- Uses a grounding-enforced RAG prompt
- Injects retrieved context with citations
- Enforces refusal when context is weak or missing
- No external APIs or vendor lock-in

**Behavior:**
- Answers are strictly source-grounded
- Citations are mandatory
- Out-of-scope queries are explicitly rejected

---

## Status

- [x] Document Ingestion
- [x] Cleaning & Normalization
- [x] Chunking
- [x] Embeddings & Vector Indexing
- [x] Retrieval Engineering (Hybrid, Reranking, Confidence)
- [x] Local LLM Integration
- [ ] Evaluation & UX Polish

---

## Design Philosophy

- Retrieval-first reasoning
- Explicit failure handling
- Explainable system behavior
- Offline, reproducible, and safe GenAI
