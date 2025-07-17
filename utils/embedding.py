"""
embedding.py
Module for generating vector embeddings for text chunks.
"""
from typing import List
from sentence_transformers import SentenceTransformer
import streamlit as st

def get_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
    """
    Load and return the embedding model (with Streamlit caching).
    Args:
        model_name: Name of the embedding model
    Returns:
        Embedding model object
    """
    @st.cache_resource(show_spinner=False)
    def load_model(name):
        return SentenceTransformer(name)
    return load_model(model_name)

def embed_texts(texts: List[str], model) -> List[list]:
    """
    Generate embeddings for a list of texts.
    Args:
        texts: List of text strings
        model: Embedding model object
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True).tolist() 