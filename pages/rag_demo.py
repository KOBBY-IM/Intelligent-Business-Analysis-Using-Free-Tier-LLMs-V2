import streamlit as st
from utils.rag_pipeline import build_rag_index, retrieve_context
from utils.embedding import get_embedding_model
from utils.prompts import build_prompt
from utils.llm_clients import get_llm_client
import os
import pandas as pd
import tempfile

# Page configuration
st.set_page_config(
    page_title="RAG LLM Demo",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 RAG-Enhanced LLM Demo")
st.markdown("""
This demo illustrates how Retrieval-Augmented Generation (RAG) enhances LLM responses for business analysis.

1. Select an industry and (optionally) upload a CSV dataset
2. Enter a business question
3. Click 'Generate Responses' to see all LLMs answer side by side
4. View the retrieved context, prompt, and generated response for each LLM
""")

# Industry selection
industry = st.selectbox(
    "Select Industry",
    ["retail", "finance"],
    help="Choose the business sector for analysis"
)

# File uploader for custom dataset
st.markdown("**Optional: Upload a custom CSV dataset for this industry**")
file_key = f"uploaded_{industry}_csv"
uploaded_file = st.file_uploader(
    f"Upload {industry.title()} CSV Dataset",
    type=["csv"],
    key=file_key
)

# Store uploaded file in session state for the industry
if uploaded_file is not None:
    # Save to a temporary file for this session
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"rag_demo_{industry}.csv")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())
    st.session_state[file_key] = temp_path
    st.success(f"Custom {industry} dataset uploaded and will be used for RAG.")

# Question input
question = st.text_input(
    "Enter your business question",
    placeholder="e.g., What are the top-selling products?",
    help="Ask a question related to the selected industry"
)

llm_options = [
    {"provider": "groq", "model": "llama3-70b-8192"},
    {"provider": "groq", "model": "moonshotai/kimi-k2-instruct"},
    {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct"},
    {"provider": "openrouter", "model": "deepseek/deepseek-r1-0528-qwen3-8b"}
]

if st.button("Generate Responses", type="primary"):
    if not question:
        st.error("Please enter a question.")
    else:
        with st.spinner("Retrieving context and generating responses from all LLMs..."):
            # Determine dataset path (uploaded or default)
            dataset_paths = {
                "retail": "data/shopping_trends_with_rag.csv",
                "finance": "data/Tesla_stock_data_with_rag.csv"
            }
            file_path = st.session_state.get(file_key)
            if not file_path:
                file_path = dataset_paths[industry]

            # Build or load RAG index (in-memory mode for Streamlit Cloud)
            rag_index = build_rag_index(
                file_path,
                dataset_type="csv",
                text_column="RAG_Text",
                persist_path=None  # In-memory only
            )
            embedding_model = get_embedding_model()
            context_chunks = retrieve_context(question, rag_index, embedding_model, top_k=5)
            prompt = build_prompt(question, context_chunks)

            # Generate responses from all LLMs
            cols = st.columns(4)
            for i, llm in enumerate(llm_options):
                with cols[i]:
                    st.markdown(f"### {llm['provider'].capitalize()}<br><span style='font-size:0.9rem'>{llm['model']}</span>", unsafe_allow_html=True)
                    try:
                        client = get_llm_client(llm["provider"], llm["model"])
                        response = client.generate(prompt)
                    except Exception as e:
                        response = f"❌ Error: {str(e)}"
                    st.subheader("LLM Response")
                    st.markdown(f'''
                        <div style="font-size: 1.0rem; line-height: 1.5; padding: 12px; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6; max-height: 350px; overflow-y: auto; min-height: 100px;">
                        {response}
                        </div>
                    ''', unsafe_allow_html=True)
else:
    st.info("Enter a question and click 'Generate Responses' to see all LLMs answer side by side.") 