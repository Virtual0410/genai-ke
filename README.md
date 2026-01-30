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

## Module 11: Evaluation & Academic Reliability Testing (Day 12)

This module focuses on **systematic evaluation** of the research assistant
to ensure reliability, safe refusal behavior, and citation discipline.

Instead of introducing new features, this stage validates whether
the system behaves responsibly under different query conditions.

---

### Evaluation Objectives

The evaluation stage verifies that the assistant:

- retrieves relevant academic sources
- prioritizes trusted documents
- cites evidence deterministically
- refuses unsupported questions
- surfaces uncertainty when sources conflict

This ensures the assistant behaves like a **responsible research tool**
rather than a speculative chatbot.

---

### Evaluation Categories

The system was tested across five query types:

#### 1. Direct Evidence Queries
Questions where answers clearly exist in the dataset.

Expected behavior:
- correct document dominance
- accurate citations
- no hallucination

---

#### 2. Cross-Document Queries
Questions requiring synthesis across multiple sources.

Expected behavior:
- retrieval of multiple trusted documents
- balanced representation of perspectives
- no forced agreement

---

#### 3. No-Evidence Queries
Questions not supported by the dataset.

Expected behavior:
- explicit refusal
- no speculative answers

---

#### 4. Conflict-Oriented Queries
Questions where sources may differ in perspective.

Expected behavior:
- conflict awareness
- no blind preference
- transparent evidence presentation

---

#### 5. Out-of-Scope Queries
Questions unrelated to the dataset.

Expected behavior:
- refusal
- no external knowledge injection

---

### Observed System Behavior

Evaluation confirmed:

- authority ranking consistently prioritizes research papers
- context selection excludes low-trust sources
- citation mapping remains deterministic
- refusal triggers correctly when evidence is insufficient
- conflict signals surface when documents compete

These results demonstrate that the assistant maintains
academic integrity and avoids hallucination by design.

---

### Limitations Identified

The evaluation process highlighted current system boundaries:

- dependent on document quality and coverage
- authority scoring remains heuristic
- conflict detection is approximate
- limited multi-hop reasoning
- no long-form argument synthesis yet

These limitations are acknowledged to maintain transparency
and guide future improvements.

---

### Key Insight

> A research assistant earns trust not by answering everything,
but by refusing responsibly and citing evidence consistently.

---

## Module 12: Multi-Hop Reasoning & Academic Synthesis (Day 13)

This module extends the research assistant from single-source retrieval
to **multi-hop reasoning across documents**.

Instead of answering questions using isolated evidence,
the system now detects when multiple sources must be combined
to produce academically meaningful responses.

---

### Motivation

Academic questions often require:

- comparing ideas across papers
- synthesizing viewpoints
- linking related concepts
- identifying patterns across sources

Single-chunk retrieval is insufficient for these tasks.

Day 13 introduces **evidence synthesis** to support
higher-level academic reasoning.

---

### Synthesis Query Detection

The assistant now identifies queries that require
cross-document reasoning using keyword signals such as:

- compare
- contrast
- across
- difference
- relationship
- synthesize
- combine

When detected, the system switches from
fact retrieval to evidence aggregation.

---

### Evidence Grouping

Retrieved chunks are grouped by document source,
allowing the assistant to:

- preserve context integrity
- avoid mixing unrelated arguments
- maintain citation traceability

This ensures synthesis remains grounded and auditable.

---

### Multi-Document Context Construction

The assistant constructs synthesis-ready context by:

- selecting top evidence from multiple trusted documents
- preserving citation mapping
- preventing low-authority sources from entering context

This enables structured academic comparisons.

---

### Observed Behavior

Testing confirmed that the assistant can:

- retrieve relevant sources across documents
- maintain authority-aware filtering
- preserve citation discipline
- avoid hallucination during synthesis
- surface multiple perspectives when appropriate

---

### Limitations

Current synthesis capabilities:

- do not perform deep argument comparison
- may include semantically adjacent but not directly comparable chunks
- rely on embedding similarity rather than conceptual understanding

These limitations guide future enhancements.

---

### Key Insight

> Academic reasoning requires connecting evidence responsibly,
not merging sources blindly.

---

### Status Update

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
- [x] Policy-Aware Context Selection
- [x] Evaluation & Reliability Testing
- [x] Multi-Hop Reasoning & Synthesis
- [ ] Argument Comparison
- [ ] Research Gap Detection
- [ ] UX Interface Layer
