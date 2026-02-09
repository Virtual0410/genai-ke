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

## Module 13: Argument Comparison & Stance Detection (Day 14)

This module introduces **stance detection** to help the research assistant
identify agreement, disagreement, and neutrality across academic sources.

Rather than blending evidence blindly, the assistant now evaluates how
documents position themselves on a topic.

---

### Motivation

Academic research rarely presents unanimous conclusions.
A responsible research assistant should:

- surface differing viewpoints
- avoid forced consensus
- preserve source attribution
- highlight uncertainty when necessary

Day 14 enables the assistant to reflect these principles.

---

### Stance Detection Logic

The assistant evaluates retrieved chunks for linguistic signals that indicate:

- **support** → benefits, improvements, effectiveness
- **question** → limitations, challenges, risks
- **mixed** → both positive and negative indicators
- **neutral** → descriptive or technical discussion

This classification helps group evidence by perspective.

---

### Stance Grouping

Retrieved chunks are grouped by stance category to:

- reveal agreement or disagreement
- prevent blending conflicting claims
- preserve academic neutrality

This allows the assistant to present balanced interpretations.

---

### Observed Behavior

Testing showed that the assistant:

- avoids inferring agreement when only one source discusses a topic
- defaults to neutral stance when evaluative language is absent
- preserves citation traceability
- surfaces uncertainty instead of speculation

This demonstrates conservative and responsible academic reasoning.

---

### Limitations

Current stance detection:

- relies on keyword heuristics
- may not capture nuanced academic arguments
- requires multiple sources for meaningful comparison
- can produce false conflict signals when topics differ

These limitations are documented for transparency and future refinement.

---

### Key Insight

> A research assistant should reveal differences in perspective,
not force agreement where evidence is limited.

---

## Module 14: Research Gap Detection (Day 15)

This module enables the research assistant to identify
areas where evidence is limited or perspectives are missing.

Rather than forcing conclusions, the assistant now surfaces
uncertainty and highlights under-explored topics.

---

### Motivation

Academic value often comes from recognizing:

- limited coverage
- missing viewpoints
- shallow evidence
- inconclusive findings

Day 15 introduces mechanisms to detect such research gaps.

---

### Gap Detection Logic

The assistant analyzes:

- number of sources discussing a topic
- stance diversity
- cross-document coverage

Signals generated include:

- limited source availability
- absence of evaluative perspectives
- insufficient comparison opportunities

---

### Observed Behavior

Testing confirmed that the assistant:

- avoids inventing conclusions
- identifies shallow evidence areas
- acknowledges when comparisons are not possible
- preserves academic caution

---

### Key Insight

> Responsible research assistants highlight what is missing,
not just what is present.

---

### Limitations

Current gap detection:

- relies on document availability
- does not infer latent research opportunities
- depends on explicit evidence patterns

These limitations guide future improvements.

---

## Day 17: Topic Coherence Filtering & Research Validity Checks

Day 17 focused on improving retrieval precision and ensuring that only
topically relevant evidence reaches the synthesis stage.

---

### Topic Coherence Filtering

A coherence filter was introduced to:
- Remove chunks loosely related to the query
- Reduce cross-topic noise
- Improve academic reliability of context selection

This prevents unrelated sections from being misinterpreted as evidence.

---

### Why Coherence Filtering Matters

Even high-similarity chunks may:
- Share vocabulary but differ in intent
- Be technically relevant but contextually misleading

Coherence filtering ensures:
- Context aligns with query intent
- Evidence remains academically valid
- Final synthesis avoids distortion

---

### Research Gap Detection Enhancement

The system now explicitly identifies:
- Lack of evaluative perspectives
- Missing comparative analysis
- Neutral-only evidence scenarios

When evidence is insufficient, the system:
- Signals a research gap
- Avoids forced conclusions
- Maintains intellectual honesty

---

### Stance Validation Refinement

Stance detection now better distinguishes:
- Support
- Questioning
- Mixed perspectives
- Neutral discussion

This improves synthesis reliability and prevents misclassification.

---

### Academic Insight Reporting Upgrade

The generated report now includes:
- Source coverage summary
- Evidence perspective analysis
- Identified research gaps
- Key contributing sources

This mirrors how literature reviews are conducted in academic research.

---

### Key Insight

High-quality GenAI systems should:
- Detect when evidence is missing
- Avoid speculative answers
- Signal uncertainty transparently

This project now reflects responsible AI behavior rather than
hallucination-prone generation.

---

### System Maturity After Day 17

The GenAI Knowledge Engine can now:
- Filter context by semantic similarity
- Validate topical coherence
- Detect stance diversity
- Identify research gaps
- Produce academically grounded synthesis context

This marks a transition from retrieval system to research assistant.

---

## Day 18: Grounded Answer Generation (Academic RAG Completion)

Day 18 transforms the system from a retrieval engine into a fully
functional academic research assistant capable of generating
source-grounded answers using a local LLM.

---

### Grounded Answer Generation Layer

A local LLM (via Ollama) is now used to generate answers strictly
from retrieved and validated context.

The answer generation module:
- Receives curated context from the retrieval pipeline
- Applies strict academic prompt rules
- Generates citation-backed answers
- Refuses to answer when evidence is insufficient

This ensures answers remain traceable and verifiable.

---

### Citation Enforcement

Generated answers must:
- Reference provided sources
- Avoid unsupported claims
- Maintain academic neutrality

If sources do not support the question, the system explicitly refuses.

---

### Refusal-First Safety Design

If retrieval confidence or context quality is low, the system responds with:

"The available sources do not provide enough evidence to answer this question."

This prevents hallucination and maintains research integrity.

---

### Academic Tone Enforcement

The system prompt enforces:
- Neutral academic language
- Evidence-based reasoning
- No speculation
- No unsupported generalization

This mimics real academic writing standards.

---

### End-to-End RAG Completion

The system now performs full pipeline reasoning:

Query  
→ Hybrid Retrieval  
→ Reranking  
→ Confidence Validation  
→ Topic Coherence Filtering  
→ Stance Detection  
→ Research Gap Detection  
→ Context Selection  
→ Context Formatting  
→ Grounded LLM Answer Generation  

---

### Key Insight

A production-grade GenAI system must:
- Control what reaches the LLM
- Control how the LLM responds
- Control when the LLM refuses

Generation is the final step — not the first.

---

### System Capability After Day 18

The GenAI Knowledge Engine can now:

- Retrieve multi-source academic evidence
- Detect stance diversity across sources
- Identify research gaps automatically
- Filter context by semantic and topical coherence
- Generate citation-grounded academic answers
- Refuse unsafe or unsupported queries
- Operate fully offline using local models

---

### Architectural Milestone

Day 18 marks the transition from:
Retrieval System → Research Reasoning System

The system now demonstrates behavior aligned with responsible AI and
academic knowledge synthesis workflows.

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
- [x] Argument Comparison & Stance Detection
- [X] Research Gap Detection
- [x] Grounded Answer Generation
- [ ] UX Interface Layer
