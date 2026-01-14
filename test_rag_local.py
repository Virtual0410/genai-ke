import json
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.retriever import Retriever
from retrieval.keyword_retriever import KeywordRetriever
from retrieval.reranker import rerank
from retrieval.confidence import has_enough_context
from llm.ollama_llm import OllamaLLM
from prompts.rag_prompt import build_rag_prompt

with open("data/processed/sample_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [c["text"] for c in chunks]
metadata = [
    {
        "chunk_id": c["chunk_id"],
        "text": c["text"],
        "source": c["source"],
        "page": c["page"]
    }
    for c in chunks
]

embedder = Embedder("all-MiniLM-L6-v2")
embeddings = embedder.embed_texts(texts)

vector_store = VectorStore(embedding_dim=embeddings.shape[1])
vector_store.add(embeddings, metadata)

semantic_retriever = Retriever(embedder, vector_store)
keyword_retriever = KeywordRetriever(metadata)

llm = OllamaLLM(model_name="mistral")

query = "What future trends in machine learning are discussed?"

semantic_results = semantic_retriever.retrieve(query)
keyword_results = keyword_retriever.retrieve(query)

combined = {}
for r in semantic_results:
    combined[r["data"]["chunk_id"]] = r

for r in keyword_results:
    cid = r["chunk_id"]
    if cid not in combined:
        combined[cid] = {
            "score": 0.4,
            "data": r
        }

final_results = list(combined.values())
final_results = rerank(final_results, query=query)

if not has_enough_context(final_results):
    print("I don't have enough information to answer.")
    exit()

top_contexts = [r["data"] for r in final_results[:3]]


prompt = build_rag_prompt(query, top_contexts)


answer = llm.generate(prompt)

print("\nANSWER:\n")
print(answer)
