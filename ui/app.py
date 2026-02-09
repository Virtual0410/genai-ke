import streamlit as st
import sys
from pathlib import Path
import traceback
import time

sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.run_query import run_query

st.set_page_config(
    page_title="Research Engine",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for query history
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

st.title("📚 Academic Research Assistant")

st.markdown("""
Ask research questions and get **evidence-grounded answers** with source tracking,
stance analysis, and research gap detection.

This system uses local LLMs (Ollama) and only answers based on available documents.
""")

# Add examples
with st.expander("📖 Example Queries"):
    st.markdown("""
    - What future trends in machine learning are discussed?
    - How is explainable AI evaluated across research papers?
    - What are the challenges in machine learning mentioned?
    - Compare federated learning and transfer learning
    - What are the applications of machine learning in healthcare?
    """)

query = st.text_input(
    "Enter Research Question",
    placeholder="What future trends in machine learning are discussed?",
    help="Ask questions about the documents in the knowledge base"
)

if st.button("🔍 Run Research", type="primary"):
    
    # Validation
    if not query or query.strip() == "":
        st.warning("⚠️ Please enter a research question.")
    elif len(query.strip()) < 10:
        st.warning("⚠️ Question too short. Please be more specific.")
    elif len(query.strip()) > 500:
        st.warning("⚠️ Question too long. Please keep it under 500 characters.")
    else:
        try:
            start_time = time.time()
            
            with st.spinner("🔄 Analyzing sources and generating answer..."):
                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔍 Retrieving relevant documents...")
                progress_bar.progress(20)
                
                result = run_query(query)
                
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
            
            elapsed = time.time() - start_time
            
            # Add to history
            st.session_state.query_history.append({
                'query': query,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'elapsed': f"{elapsed:.2f}s"
            })
            
            # Check if answer indicates failure
            answer = result.get("answer", "")
            
            if not answer or answer.strip() == "":
                st.error("❌ No answer generated. Please try a different question.")
                
            elif any(phrase in answer.lower() for phrase in [
                "not provide enough evidence",
                "insufficient",
                "no trusted context",
                "do not provide strong"
            ]):
                st.warning("⚠️ Limited Evidence")
                st.info(answer)
                
                if result.get("report"):
                    with st.expander("📋 See Analysis Details"):
                        st.text(result["report"])
                        
            else:
                # SUCCESS - Show full results
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.success("✅ Answer Generated")
                with col2:
                    st.caption(f"⏱️ {elapsed:.2f}s")
                
                st.divider()
                
                # ===== FINAL ANSWER =====
                st.subheader("📘 Answer")
                st.markdown(answer)
                
                # ===== SOURCES =====
                sources = result.get("sources", [])
                if sources:
                    st.subheader("📚 Sources Used")
                    
                    unique_sources = list(set(
                        (s["doc_name"], s["page"])
                        for s in sources
                    ))
                    
                    for doc, page in unique_sources:
                        st.markdown(f"- **{doc}** (page {page})")
                else:
                    st.info("No specific sources cited")
                
                # ===== REPORT =====
                report = result.get("report", "")
                if report:
                    st.subheader("🧪 Research Insight Report")
                    st.text(report)
                
                # ===== STANCE =====
                stance = result.get("stance", {})
                if stance:
                    st.subheader("⚖️ Evidence Perspective")
                    
                    cols = st.columns(4)
                    cols[0].metric("Support", len(stance.get("support", [])))
                    cols[1].metric("Question", len(stance.get("question", [])))
                    cols[2].metric("Mixed", len(stance.get("mixed", [])))
                    cols[3].metric("Neutral", len(stance.get("neutral", [])))
                    
                    with st.expander("📊 Raw Evidence Details"):
                        st.json(stance)
                
                # ===== CONTEXT DEBUG =====
                context = result.get("context", "")
                if context:
                    with st.expander("🔍 Context Used (Debug)"):
                        st.text(context)
        
        except FileNotFoundError as e:
            st.error(f"❌ Data file not found: {e}")
            st.info("Make sure the processed data files exist in data/processed/")
            
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            with st.expander("🐛 Error Details"):
                st.code(traceback.format_exc())
            st.info("Please check that Ollama is running and the model is available.")

# Sidebar info
with st.sidebar:
    st.header("ℹ️ System Info")
    st.markdown("""
    **Model:** Mistral (Ollama)
    
    **Features:**
    - Hybrid retrieval (semantic + keyword)
    - Authority-aware ranking
    - Stance detection
    - Research gap identification
    - Grounded generation
    
    **Status:**
    - Uses local embeddings
    - No external API calls
    - Fully offline capable
    """)
    
    st.divider()
    
    # Query History
    if st.session_state.query_history:
        st.subheader("📜 Query History")
        for i, item in enumerate(reversed(st.session_state.query_history[-5:]), 1):
            with st.expander(f"{i}. {item['query'][:40]}..."):
                st.caption(f"Time: {item['timestamp']}")
                st.caption(f"Duration: {item['elapsed']}")
        
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()
    
    st.divider()
    st.caption("GenAI Knowledge Engine v1.0")
