"""
rag_pipeline.py
Orchestrates the full RAG pipeline: loading, chunking, embedding, storing, retrieving.
"""
from typing import List, Dict, Any
from utils.data_loader import load_csv_dataset, load_text_dataset
from utils.chunking import chunk_documents
from utils.embedding import get_embedding_model, embed_texts
from utils.vector_db import VectorDB

def build_rag_index(dataset_path: str, dataset_type: str = "csv", text_column: str = None, chunk_size: int = 500, overlap: int = 50, persist_path: str = None) -> VectorDB:
    """
    Build the RAG index from a dataset (CSV or text).
    Args:
        dataset_path: Path to the dataset file
        dataset_type: "csv" or "text"
        text_column: Optional column name for CSV
        chunk_size: Chunk size for splitting text
        overlap: Overlap between chunks
        persist_path: Optional path for vector DB persistence
    Returns:
        VectorDB object with indexed data
    """
    # Load data
    if dataset_type == "csv":
        docs = load_csv_dataset(dataset_path, text_column=text_column)
    elif dataset_type == "text":
        docs = load_text_dataset(dataset_path)
    else:
        raise ValueError("Unsupported dataset type: must be 'csv' or 'text'")
    # Chunk documents
    chunks = chunk_documents(docs, chunk_size=chunk_size, overlap=overlap)
    # Get embedding model
    model = get_embedding_model()
    # Embed chunks
    embeddings = embed_texts(chunks, model)
    # Prepare metadata
    metadatas = [{"text": chunk, "chunk_id": i} for i, chunk in enumerate(chunks)]
    # Build vector DB
    vector_db = VectorDB(persist_path=persist_path)
    vector_db.add_documents(embeddings, metadatas)
    return vector_db

def retrieve_context(query: str, vector_db: VectorDB, embedding_model: Any, top_k: int = 5) -> List[Dict]:
    """
    Retrieve relevant context chunks for a query.
    Args:
        query: User/business query string
        vector_db: VectorDB object
        embedding_model: Embedding model object
        top_k: Number of chunks to retrieve
    Returns:
        List of metadata dicts for top results
    """
    query_embedding = embed_texts([query], embedding_model)[0]
    return vector_db.query(query_embedding, top_k=top_k) 