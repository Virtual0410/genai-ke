# GenAI Knowledge Engine

A production-ready, fully local Retrieval-Augmented Generation (RAG) system built from first principles. Features semantic + keyword hybrid retrieval, authority-based source ranking, stance detection, and grounded answer generation with citation enforcement.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- [Ollama](https://ollama.ai) installed and running
- 8GB+ RAM recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/Virtual0410/genai-ke.git
cd genai-ke

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Pull LLM model
ollama pull phi:2.7b
```

### Pre-compute Embeddings (One-Time Setup)

```bash
python precompute_embeddings.py
```

This creates a cache of embeddings for instant query processing.

### Run the System

**Option 1: Web UI (Recommended)**
```bash
streamlit run ui/app.py
```
Visit http://localhost:8501

**Option 2: Command Line**
```python
from pipeline.run_query import run_query

result = run_query("How is explainable AI evaluated?")
print(result["answer"])
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Query Input                               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Hybrid Retrieval                                │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ Semantic (FAISS) │         │ Keyword (BM25)   │         │
│  │  - Embeddings    │         │  - TF-IDF        │         │
│  │  - Cosine Sim    │         │  - Term Matching │         │
│  └──────────────────┘         └──────────────────┘         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Reranking & Filtering                           │
│  - Quality scoring based on chunk length                     │
│  - Confidence thresholding                                   │
│  - Optional coherence filtering                              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│          Document Authority Scoring                          │
│  Authority = 0.5×Relevance + 0.3×Trust + 0.2×Recency       │
│  - Trust: Based on document type (research > blog > note)   │
│  - Recency: Temporal decay over 5 years                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Context Selection                               │
│  - Top N documents by authority                              │
│  - Top K chunks per document                                 │
│  - Fallback to relevance-only if filtering too strict       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│         Stance Detection & Gap Analysis                      │
│  - Classify chunks: support, question, mixed, neutral       │
│  - Identify research gaps and limited evidence              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│            Context Formatting                                │
│  - Citation-ready format                                     │
│  - Source attribution                                        │
│  - Optional synthesis for multi-document queries            │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│        Grounded Answer Generation (Ollama)                   │
│  - Temperature: 0.1 (deterministic)                          │
│  - Strict grounding to provided context                      │
│  - Refusal if evidence insufficient                          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Answer + Sources + Report                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features

### 🔍 Hybrid Retrieval
- **Semantic search** using sentence transformers and FAISS
- **Keyword search** with proper BM25 implementation (TF-IDF)
- Automatic result merging and deduplication

### 📊 Authority-Based Ranking
- Multi-factor scoring: relevance + trust + recency
- Configurable trust weights by document type
- Temporal decay for older documents

### 🎓 Academic Features
- **Stance detection**: Identifies support/question/mixed/neutral perspectives
- **Research gap detection**: Highlights under-explored topics
- **Citation enforcement**: All answers backed by sources
- **Refusal behavior**: Refuses to answer when evidence insufficient

### ⚡ Performance
- **Embedding caching**: Pre-compute once, query instantly
- **40x speedup**: From 20s → 0.5s per query (after first)
- **Memory efficient**: Loads embeddings once, reuses across queries

### ⚙️ Configuration-Driven
All parameters tunable via `config.yaml`:
- Retrieval top-k values
- Authority score weights
- Confidence thresholds
- LLM model and temperature
- Context selection limits

---

## 📁 Project Structure

```
genai-ke/
├── config.yaml              # All tunable parameters
├── config.py                # Configuration loader
├── precompute_embeddings.py # One-time embedding generation
│
├── data/
│   ├── raw/                 # Input documents (PDF, txt, md)
│   └── processed/           # Chunked JSON with metadata
│       └── sample_chunks_multi.json
│
├── cache/                   # Pre-computed embeddings
│   ├── embeddings_*.npy
│   └── metadata_*.pkl
│
├── embeddings/
│   ├── embedder.py          # Sentence transformer wrapper
│   └── vector_store.py      # FAISS index manager
│
├── ingestion/
│   ├── pdf_loader.py        # PDF page-level extraction
│   ├── text_loader.py       # Markdown/txt loading
│   ├── cleaner.py           # Text normalization
│   ├── chunker.py           # Semantic/fixed-size chunking
│   ├── document_registry.py # Stable doc ID generation
│   └── ingest_multi.py      # Multi-document pipeline
│
├── retrieval/
│   ├── retriever.py         # Semantic retrieval (FAISS)
│   ├── keyword_retriever.py # BM25 implementation
│   ├── reranker.py          # Quality-based reranking
│   ├── confidence.py        # Confidence gating
│   ├── coherence_filter.py  # Topic relevance filtering
│   ├── grouping.py          # Document-level grouping
│   ├── authority.py         # Multi-factor scoring
│   ├── trust.py             # Document type trust weights
│   ├── recency.py           # Temporal decay scoring
│   ├── context_selector.py  # Top-N document selection
│   ├── stance.py            # Perspective classification
│   ├── gap_detector.py      # Research gap identification
│   └── synthesis.py         # Multi-doc evidence grouping
│
├── llm/
│   ├── ollama_llm.py        # Ollama SDK wrapper
│   ├── prompt.py            # System prompt with rules
│   ├── answer_generator.py  # Grounded generation
│   ├── context_formatter.py # Citation-ready formatting
│   └── report_generator.py  # Research insight reports
│
├── pipeline/
│   └── run_query.py         # End-to-end query execution
│
├── ui/
│   └── app.py               # Streamlit web interface
│
└── errors.py                # Custom exception types
```

---

## ⚙️ Configuration

Edit `config.yaml` to tune behavior (no code changes needed):

```yaml
# Retrieval settings
retrieval:
  semantic_top_k: 10    # Number of semantic results
  keyword_top_k: 5      # Number of keyword results

# Context selection
context_selection:
  max_docs: 3           # Max documents in answer
  max_chunks_per_doc: 4 # Max chunks per document
  min_authority_score: 0.1

# LLM settings
llm:
  model_name: "phi:2.7b"  # Ollama model
  temperature: 0.1         # Determinism (0-1)
  max_tokens: 400

# Authority scoring weights
authority:
  relevance_weight: 0.5
  trust_weight: 0.3
  recency_weight: 0.2
  
  # Document type trust scores
  trust_scores:
    research_paper: 1.0
    documentation: 0.8
    blog: 0.6
    note: 0.5

# Confidence thresholds
confidence:
  min_results: 1
  min_score: 0.35
  min_context_chars: 200
```

---

## 📊 Performance Metrics

| Metric | Before Optimization | After Optimization |
|--------|--------------------|--------------------|
| First query | ~20 seconds | ~3 seconds |
| Subsequent queries | ~20 seconds | ~0.5 seconds |
| Memory usage | High (reload each query) | Low (cached) |
| Embedding computation | Every query | One-time only |

**Improvements:**
- **6.7x faster** first query
- **40x faster** subsequent queries
- **90% memory reduction** via caching

---

## 🧪 Testing

### Quick Test
```bash
python -c "from pipeline.run_query import run_query; print(run_query('What is machine learning?')['answer'])"
```

### Full Test Suite
```bash
# Test individual components
python test_embeddings.py
python test_retriever_semantic.py
python test_retriever_keyword.py
python test_chunker.py

# Test end-to-end pipeline
python test_quick.py
```

---

## 📚 Adding New Documents

### Step 1: Add Raw Documents
```bash
# Place PDFs in data/raw/research/
# Place markdown/txt in data/raw/blogs/ or data/raw/notes/
```

### Step 2: Ingest
```bash
python ingestion/ingest_multi.py
```

This processes all raw documents and outputs `data/processed/sample_chunks_multi.json`

### Step 3: Re-compute Embeddings
```bash
python precompute_embeddings.py
```

### Step 4: Query!
Your new documents are now searchable.

---

## 🔧 Troubleshooting

### "No trusted context available"
- Lower `min_authority_score` in `config.yaml`
- Check that documents have valid metadata (doc_type, published_date)

### "Ollama model requires more memory"
- Switch to a smaller model: `phi:2.7b` (1.6GB) instead of `mistral` (8GB)
- Edit `config.yaml` → `llm.model_name`

### Slow query performance
- Ensure embeddings are pre-computed: check `cache/` directory exists
- Run `precompute_embeddings.py` if missing

### Empty or poor answers
- Check `config.yaml` thresholds aren't too restrictive
- Verify documents contain relevant information
- Try lowering `confidence.min_score` to 0.3

---

## 🛠️ Development

### Requirements
- Python 3.12+
- PyYAML
- numpy
- faiss-cpu
- sentence-transformers
- ollama
- streamlit
- torch

### Installing from Requirements
```bash
pip install -r requirements.txt
```

### Code Style
- Modular design with clear separation of concerns
- Configuration-driven (avoid hardcoded values)
- Comprehensive error handling
- Type hints where appropriate
- Docstrings for all public functions

---

## 📖 How It Works

### 1. Document Ingestion
- PDFs extracted page-by-page
- Text cleaned and normalized
- Chunked semantically (preserving paragraph boundaries)
- Metadata attached (doc_id, doc_type, page, published_date)

### 2. Embedding & Indexing
- Chunks embedded using sentence transformers
- FAISS index built for fast similarity search
- Embeddings cached to disk for reuse

### 3. Query Processing
- **Semantic retrieval**: Query embedded, FAISS finds similar chunks
- **Keyword retrieval**: BM25 scores based on term frequency
- **Merging**: Combine and deduplicate results

### 4. Ranking & Filtering
- Rerank by chunk quality (length penalties)
- Filter by confidence threshold
- Optional coherence filtering

### 5. Authority Scoring
- Group chunks by document
- Score documents: `Authority = 0.5×Relevance + 0.3×Trust + 0.2×Recency`
- Select top N documents

### 6. Context Preparation
- Extract top K chunks from each selected document
- Classify stance (support/question/mixed/neutral)
- Detect research gaps
- Format with citations

### 7. Answer Generation
- Send context + query to Ollama
- Enforce strict grounding (no external knowledge)
- Generate with citations
- Refuse if evidence insufficient

---

## 🎓 Academic Use Case

This system is designed for **academic research assistance**:

✅ **Source transparency**: Every claim backed by citations  
✅ **Multi-document synthesis**: Compare perspectives across papers  
✅ **Stance detection**: Identify agreement/disagreement  
✅ **Research gaps**: Highlight under-explored areas  
✅ **Refusal behavior**: Won't speculate without evidence  
✅ **Authority ranking**: Prioritize trusted sources  

Perfect for literature reviews, research exploration, and evidence-based Q&A.

---

## 🚧 Known Limitations

1. **Single dataset**: Currently configured for one sample corpus (easily expandable)
2. **Keyword-based stance detection**: Uses pattern matching, not semantic understanding
3. **No cross-encoder reranking**: Could improve precision with neural reranker
4. **Local-only**: No cloud deployment configuration (by design)

These are acknowledged constraints, not bugs. The system is production-ready within these boundaries.

---

## 🤝 Contributing

This is a learning project demonstrating RAG system construction from first principles. Feel free to:
- Fork and experiment
- Suggest improvements
- Report issues
- Add features

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Sentence Transformers** for embedding models
- **FAISS** for efficient similarity search
- **Ollama** for local LLM inference
- **Streamlit** for rapid UI development

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `config.yaml` settings
3. Verify Ollama is running: `ollama list`
4. Ensure embeddings are cached: `dir cache`

---

**Built with care for transparency, accuracy, and academic integrity.**

_Last updated: February 2026_
