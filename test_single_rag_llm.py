from utils.rag_pipeline import build_rag_index, retrieve_context
from utils.embedding import get_embedding_model
from utils.llm_clients import get_llm_client
from utils.prompts import build_prompt

# Test parameters
industry = "retail"
dataset_path = "data/shopping_trends.csv"
question = "Which regions underperformed last quarter and why?"

# Build RAG index and embedding model
print("Building RAG index...")
rag_index = build_rag_index(dataset_path, dataset_type="csv")
embedding_model = get_embedding_model()

# Retrieve context
print("Retrieving context...")
context_results = retrieve_context(question, rag_index, embedding_model, top_k=3)
context_chunks = [r["text"] for r in context_results]

# Build prompt
prompt = build_prompt(question, context_chunks)

# Choose LLM (Groq Llama3-70b-8192)
llm = get_llm_client("groq", "llama3-70b-8192")

# Generate response
print("Calling LLM...")
response = llm.generate(prompt)

print("\nPrompt:\n", prompt)
print("\nLLM Response:\n", response) 