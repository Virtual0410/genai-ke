# GenAI Knowledge Engine

A fully local, end-to-end Retrieval-Augmented Generation (RAG) system
built from first principles, focusing on data quality, semantic retrieval,
traceability, and hallucination control.

This project incrementally constructs the core components of a
production-grade GenAI system instead of relying on black-box APIs.

---

## Architecture Overview

Raw Documents (PDFs, Markdown, Text)<br>
↓<br>
Document Registration & Page-Level Ingestion<br>
↓<br>
Text Cleaning & Normalization<br>
↓<br>
Semantic Chunking with Source Metadata<br>
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
to keep the pipeline reproducible, inspectable, and easy to review.

---

## Module 1: Document Ingestion

- Ingests documents page-by-page
- Supports multiple formats (PDF, Markdown, Text)
- Preserves source filename and page numbers
- Produces a consistent internal document representation

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

This enables precise citations and systematic debugging.

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

## Module 7: Multi-Document Ingestion & Source Identity

This module upgrades the system from single-document RAG to a
**multi-document, source-aware architecture**.

The focus is on preserving **document identity and provenance**
so that downstream components can reason across sources reliably.

---

### Document Registry

Each document is registered with stable metadata:

- `doc_id` (deterministic, hash-based)
- `doc_name`
- `doc_type` (research paper, blog, notes, etc.)
- `published_date`

This guarantees:
- consistent document identity across runs
- traceability of every chunk
- a foundation for trust and recency-aware retrieval

---

### Multi-Document Ingestion

- Supports ingesting multiple documents of different types
- Documents are explicitly declared and registered
- All documents are processed uniformly into a shared chunk space

---

### Chunking with Ownership

Text chunking remains a **pure operation**:
- `chunker.py` only splits raw text
- No document or metadata logic inside chunking

Document ownership and metadata are attached **after chunking** during ingestion.

Each chunk contains:
- `chunk_id` (globally unique)
- `doc_id`
- `doc_name`
- `doc_type`
- `published_date`
- `page`
- `text`

---

### Output

A new processed dataset is generated:
This dataset replaces the single-document chunk file for all subsequent
retrieval and generation stages.

**Key insight:**  
Multi-source reasoning begins with disciplined document identity,
not more sophisticated models.

---

## Module 8: Source-Aware Retrieval & Document-Level Reasoning

This module upgrades retrieval from **chunk-level ranking**
to **document-aware evidence aggregation**.

Instead of treating all retrieved chunks equally,
the system now reasons about *which documents dominate the answer space*.

---

### Motivation

Pure chunk-level retrieval fails when:
- multiple documents contribute conflicting information
- newer but less reliable sources overshadow research
- relevance must be explained, not just ranked

introduces **document-level reasoning** to address these issues.

---

### Document-Level Grouping

Retrieved chunks are grouped by `doc_id`:

- All chunks from the same document are aggregated
- Document-level statistics are computed:
  - maximum relevance score
  - average relevance score
  - number of contributing chunks

This enables the system to answer:
> “Which sources actually support this answer?”

---

### Document-Level Scoring

For each document, the system computes:

- `max_score`: strongest supporting evidence
- `avg_score`: overall relevance consistency
- `chunk_count`: coverage depth

Documents now *compete as sources*, not just as isolated chunks.

---

### Source-Aware Retrieval Output

The retrieval pipeline now produces:

1. A **document-level summary**  
   (which sources dominate and why)

2. A **chunk-level breakdown**  
   (traceable evidence with page numbers)

This makes retrieval behavior:
- explainable
- debuggable
- auditable

---

### Design Principle

> Retrieval quality improves when documents compete, not individual chunks.

establishes the foundation for:
- trust weighting
- recency bias
- conflict detection
- source prioritization

These are implemented in subsequent modules.

---

## Module 9: Authority-Aware Retrieval (Trust, Recency & Conflict Resolution)

This module introduces **decision policy** into the retrieval system.

Instead of ranking sources purely by semantic similarity,
the system now evaluates *which sources should be trusted more*,
*which should be preferred due to recency*, and
*when multiple sources disagree*.

---

### Motivation

Pure relevance-based retrieval fails in real-world settings:

- Blogs may be newer but less reliable than research papers
- Notes may be most recent but incomplete or informal
- Multiple sources may provide conflicting perspectives

Day 10 formalizes **authority-aware retrieval** to address these issues.

---

### Trust Policy

Each document type is assigned an explicit trust weight:

- `research_paper` → highest trust
- `blog` → medium trust
- `notes` → lowest trust

Trust is treated as a **policy decision**, not a learned parameter,
making system behavior transparent and auditable.

---

### Recency Scoring

Documents are scored based on publication date using:

- bounded linear decay
- capped influence (older documents never dominate negatively)
- explainable behavior

Recency influences ranking without overriding trust or relevance.

---

### Authority Score

Each document receives a final **authority score** combining:

- semantic relevance (from retrieval)
- trust weight (document type)
- recency score (publication date)

This score determines **which sources dominate the answer space**.

Authority scoring ensures:
- trusted sources are preferred
- newer information is considered
- relevance remains the primary signal

---

### Conflict Detection

When multiple documents provide similarly strong support,
the system flags a **potential conflict** instead of silently choosing one.

This allows downstream components to:
- surface uncertainty
- request clarification
- present multiple perspectives when appropriate

---

### Outcome

Retrieval output now includes:

1. **Document authority ranking**
2. **Document-level evidence summaries**
3. **Traceable chunk-level citations**
4. **Explicit conflict signals**

This enables safe, explainable, and policy-driven context selection
for grounded generation.

---

### Status Update

- [x] Document Ingestion
- [x] Cleaning & Normalization
- [x] Chunking
- [x] Embeddings & Vector Indexing
- [x] Hybrid Retrieval & Reranking
- [x] Hallucination Control
- [x] Local LLM Integration
- [x] Multi-Document Ingestion & Metadata
- [x] Source-Aware Retrieval
- [x] **Authority-Aware Retrieval (Trust & Recency)**
- [x] **Conflict Detection**
- [ ] Policy-Aware Context Selection
- [ ] Citation-Controlled Generation
- [ ] Feedback & Learning Loop

