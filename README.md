# GenAI Knowledge Engine

A fully local, end-to-end Retrieval-Augmented Generation (RAG) system
built from first principles, focusing on data quality, semantic retrieval,
source traceability, and hallucination control.

This project incrementally constructs a **production-grade GenAI system**
without relying on black-box APIs, emphasizing explainability,
policy enforcement, and safe generation.

---

## Architecture Overview

Raw Documents (PDF / Markdown / Text)<br>
↓<br>
Document Registration & Page-Level Ingestion<br>
↓<br>
Text Cleaning & Normalization<br>
↓<br>
Semantic Chunking → Source Metadata Attachment<br>
↓<br>
Embeddings & Vector Search (FAISS)<br>
↓<br>
Hybrid Retrieval (Semantic + Keyword)<br>
↓<br>
Reranking & Confidence Gate<br>
↓<br>
Source-Aware Retrieval & Authority Scoring<br>
↓<br>
Policy-Aware Context Selection & Citations<br>
↓<br>
Local LLM (Ollama) — Grounded Answer or Refusal

---

**Note:**  
Small processed datasets are included under `data/processed/`
to keep the pipeline reproducible and reviewable.

---

## Module 1: Document Ingestion

- Ingests documents page-by-page
- Supports PDFs, Markdown, and plain text
- Preserves source filename and page numbers
- Produces a consistent internal schema

**Why page-level ingestion?**  
Enables precise citations, debugging, and traceability of generated answers.

---

## Module 2: Text Cleaning & Normalization

- Removes headers, footers, and page artifacts
- Normalizes whitespace and broken lines
- Preserves semantic meaning and metadata

**Design principle:**  
Cleaning is isolated from ingestion to allow iterative improvement
without reprocessing raw data.

---

## Module 3: Chunking Strategy

Text is split into retrievable knowledge units.

### Semantic Chunking
- Splits text along paragraph/section boundaries
- Preserves semantic coherence
- Reduces embedding dilution

Chunking is intentionally **pure**:
- No document metadata
- No policy logic

Metadata is attached during ingestion.

**Key insight:**  
Chunking is a retrieval decision, not a preprocessing afterthought.

---

## Module 4: Embeddings & Vector Search

### Embedding Generation
- Local SentenceTransformers
- Evaluated multiple models
- Final model selected based on ranking stability

### Vector Indexing
- FAISS (cosine similarity)
- Deterministic, local, inspectable

**Key insight:**  
Embeddings decide *what can be retrieved*, not *what is correct*.

---

## Module 5: Retrieval Engineering

### Hybrid Retrieval
- Semantic retrieval (FAISS)
- Keyword retrieval (BM25-lite)
- Merge & deduplicate by `chunk_id`

### Reranking
- Penalizes overly generic chunks
- Boosts intent-aligned sections
- Prefers information-dense content

### Confidence Gate
- Refuses to answer when context quality is insufficient

> “I don’t know” is treated as a feature, not a failure.

---

## Module 6: Local LLM Integration

- Fully local LLM (Ollama)
- Grounding-enforced prompt
- No external APIs
- Refusal on weak or missing context

---

## Module 7: Multi-Document Ingestion & Source Identity

- Multiple documents ingested uniformly
- Deterministic `doc_id` assignment
- Metadata preserved:
  - document type
  - publication date
  - source name

This enables cross-document reasoning.

**Key insight:**  
Multi-source reasoning begins with disciplined document identity.

---

## Module 8: Source-Aware Retrieval

- Retrieval results grouped by document
- Document-level statistics computed:
  - max relevance
  - average relevance
  - coverage depth

Documents compete as sources, not isolated chunks.

---

## Module 9: Authority-Aware Retrieval (Trust, Recency & Conflict)

### Trust Policy
- Explicit trust weights by document type
- Transparent and tunable

### Recency Scoring
- Bounded temporal decay
- Prevents recency from overriding trust

### Authority Score
Combines:
- relevance
- trust
- recency

### Conflict Detection
- Flags competing sources with similar authority
- Avoids silent disagreement

**Key insight:**  
Truth in RAG is a policy decision, not a similarity score.

---

## Module 10: Policy-Aware Context Selection & Citations

- Context selected **only** from top-authority documents
- Explicit context budget enforced
- Lower-authority sources excluded
- Citation-ready context construction
- Deterministic reference mapping

If no trusted context exists:
→ the system refuses to answer.

**Key insight:**  
Safety is decided before the model ever sees the prompt.

---

## Status

- [x] Document Ingestion
- [x] Cleaning & Normalization
- [x] Chunking
- [x] Embeddings & Vector Indexing
- [x] Hybrid Retrieval & Reranking
- [x] Confidence Gating
- [x] Local LLM Integration
- [x] Multi-Document Ingestion
- [x] Source-Aware Retrieval
- [x] Authority-Aware Retrieval
- [x] Policy-Aware Context Selection & Citations
- [ ] Evaluation & Stress Testing
- [ ] Feedback & Learning Loop
- [ ] UX & Interface Layer

---

## Design Philosophy

- Retrieval-first reasoning
- Explicit failure handling
- Explainable system behavior
- No hallucination by construction
- Offline, reproducible, and safe GenAI
