# Quick Start Guide

## Prerequisites

1. **Python 3.12** installed
2. **Ollama** installed and running
   - Download from: https://ollama.ai
   - Pull Mistral model: `ollama pull mistral`

## Setup

```bash
# Clone or navigate to project
cd genai-ke

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Verify Ollama

```bash
# Check Ollama is running
ollama list

# Should show mistral model
# If not, pull it:
ollama pull mistral
```

## Running the System

### Option 1: Web UI (Recommended)

```bash
streamlit run ui/app.py
```

Then open browser to: http://localhost:8501

### Option 2: Python Script

```python
from pipeline.run_query import run_query

result = run_query("What future trends in machine learning are discussed?")
print(result["answer"])
```

### Option 3: Test Scripts

```bash
# Test Ollama integration
python test_ollama_direct.py

# Test full pipeline
python test_full_pipeline.py
```

## Common Issues

### Unicode Errors
**Fixed!** The system now handles UTF-8 encoding properly.

### Ollama Connection Error
```bash
# Make sure Ollama is running:
ollama serve

# In another terminal, test:
ollama run mistral "Hello"
```

### Empty Answers
- Check that `data/processed/sample_chunks_multi.json` exists
- Verify Ollama model is responding: `python test_ollama_direct.py`
- Check Ollama logs for errors

### Import Errors
```bash
# Make sure you're in venv:
.\venv\Scripts\activate

# Reinstall dependencies:
pip install -r requirements.txt
```

## Project Structure

```
genai-ke/
├── data/
│   ├── processed/          # Processed document chunks
│   └── raw/               # Raw documents (populate this!)
├── embeddings/            # Embedding & vector store
├── ingestion/             # Document loading & chunking
├── retrieval/             # Retrieval & ranking logic
├── llm/                   # LLM integration
├── pipeline/              # End-to-end query pipeline
├── ui/                    # Streamlit interface
├── config.py              # Configuration settings
└── requirements.txt       # Python dependencies
```

## Adding Documents

1. Place documents in `data/raw/`
   - PDFs: `data/raw/research/`
   - Markdown: `data/raw/blogs/` or `data/raw/notes/`

2. Run ingestion:
   ```python
   from ingestion.ingest_multi import ingest_directory
   
   ingest_directory(
       "data/raw/research",
       output_path="data/processed/my_chunks.json"
   )
   ```

3. Update `config.py` to point to your new chunks file

## Configuration

Edit `config.py` to customize:
- LLM model and parameters
- Retrieval settings
- Authority weights
- Confidence thresholds

## Example Queries

Good queries:
- "What future trends in machine learning are discussed?"
- "How is explainable AI evaluated?"
- "What challenges does the paper mention?"

Bad queries:
- "Tell me everything" (too broad)
- "What will happen in 2030?" (speculation not in sources)
- "Explain quantum physics" (if not in your documents)

## System Behavior

The system will:
✅ Answer when confident evidence exists
✅ Cite sources with page numbers
✅ Refuse when evidence is insufficient
✅ Identify research gaps
✅ Detect stance across sources

The system will NOT:
❌ Make up answers
❌ Speculate beyond sources
❌ Use external knowledge
❌ Generalize without evidence

## Troubleshooting

### Slow Response
- Embedding generation is slow on first run (cached after)
- Ollama model loading takes time on first query
- Consider using smaller embedding model in `config.py`

### Out of Memory
- Reduce `MAX_CHUNKS_PER_DOC` in `config.py`
- Use smaller LLM model (try `phi:2.7b`)
- Process fewer documents

### Poor Answer Quality
- Check that query matches document content
- Verify sources are being retrieved (check debug output)
- Try adjusting `LLM_TEMPERATURE` in `config.py`
- Ensure using Mistral not Phi (Mistral is better for this task)

## Next Steps

1. Add your own documents to `data/raw/`
2. Run ingestion to process them
3. Test with queries related to your documents
4. Adjust configuration as needed

## Support

Check `FIXES_APPLIED.md` for recent changes and known issues.
