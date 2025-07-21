import streamlit as st
from utils.rag_pipeline import build_rag_index, retrieve_context
from utils.embedding import get_embedding_model
from utils.prompts import build_prompt
from utils.llm_clients import get_llm_client
import os
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="RAG LLM Demo",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 RAG-Enhanced LLM Demo")
st.markdown("""
This demo illustrates how Retrieval-Augmented Generation (RAG) enhances LLM responses for business analysis.

1. Select an industry and enter a business question
2. Choose an LLM model
3. See retrieved context from the dataset
4. View the generated response
""")

# Industry selection
industry = st.selectbox(
    "Select Industry",
    ["retail", "finance"],
    help="Choose the business sector for analysis"
)

# Question input
question = st.text_input(
    "Enter your business question",
    placeholder="e.g., What are the top-selling products?",
    help="Ask a question related to the selected industry"
)

# LLM selection
llm_options = [
    {"provider": "groq", "model": "llama3-70b-8192"},
    {"provider": "groq", "model": "moonshotai/kimi-k2-instruct"},
    {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct"},
    {"provider": "openrouter", "model": "deepseek/deepseek-r1-0528-qwen3-8b"}
]
selected_llm = st.selectbox(
    "Select LLM Model",
    [f"{llm['provider']}: {llm['model']}" for llm in llm_options]
)

if st.button("Generate Response", type="primary"):
    if not question:
        st.error("Please enter a question.")
    else:
        with st.spinner("Retrieving context and generating response..."):
            # Get dataset path
            dataset_paths = {
                "retail": "data/shopping_trends_with_rag.csv",
                "finance": "data/Tesla_stock_data_with_rag.csv"
            }
            dataset_path = dataset_paths[industry]
            
            # Build or load RAG index (in-memory mode for Streamlit Cloud)
            rag_index = build_rag_index(
                dataset_path,
                dataset_type="csv",
                text_column="RAG_Text",
                persist_path=None  # In-memory only
            )
            
            # Get embedding model
            embedding_model = get_embedding_model()
            
            # Retrieve context
            context_chunks = retrieve_context(question, rag_index, embedding_model, top_k=5)
            
            # Build prompt
            prompt = build_prompt(question, context_chunks)
            
            # Get LLM client
            selected_idx = [i for i, opt in enumerate(llm_options) if f"{opt['provider']}: {opt['model']}" == selected_llm][0]
            llm = llm_options[selected_idx]
            client = get_llm_client(llm["provider"], llm["model"])
            
            # Generate response
            response = client.generate(prompt)
            
            # Display results
            st.subheader("Retrieved Context")
            for i, chunk in enumerate(context_chunks, 1):
                with st.expander(f"Context Chunk {i}"):
                    st.json(chunk)
            
            st.subheader("Generated Prompt")
            st.text_area("Prompt", prompt, height=200)
            
            st.subheader("LLM Response")
            st.markdown(response)
else:
    st.info("Enter a question and select an LLM to generate a response.") 