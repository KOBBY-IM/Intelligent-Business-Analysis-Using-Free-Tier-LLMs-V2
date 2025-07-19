"""
rag_pipeline.py
Orchestrates the full RAG pipeline: loading, chunking, embedding, storing, retrieving.
"""
from typing import List, Dict, Any
from utils.data_loader import load_csv_dataset, load_text_dataset
from utils.chunking import chunk_documents
from utils.embedding import get_embedding_model, embed_texts
from utils.vector_db import VectorDB
import pandas as pd

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
    print(f"Loading data from {dataset_path}, type: {dataset_type}, text_column: {text_column}")
    # Load data
    if dataset_type == "csv":
        docs = load_csv_dataset(dataset_path, text_column=text_column)
    elif dataset_type == "text":
        docs = load_text_dataset(dataset_path)
    else:
        raise ValueError(f"Unsupported dataset_type: {dataset_type}")
    print(f"Loaded {len(docs)} documents.")
    if docs:
        print(f"First document snippet: {docs[0][:100]}...")
    # Chunk documents
    chunks = chunk_documents(docs, chunk_size=chunk_size, overlap=overlap)
    print(f"Chunked into {len(chunks)} chunks.")
    # Get embedding model
    model = get_embedding_model()
    # Embed chunks
    embeddings = embed_texts(chunks, model)
    print(f"Preparing metadatas for {len(chunks)} chunks.")
    # Prepare metadata with additional fields for traceability
    # Try to load the DataFrame for metadata if possible
    df = None
    try:
        if dataset_type == "csv":
            df = pd.read_csv(dataset_path)
    except Exception:
        pass
    metadatas = []
    for i, chunk in enumerate(chunks):
        meta = {"text": chunk, "chunk_id": i}
        if df is not None and i < len(df):
            row = df.iloc[i]
            # Add key fields for traceability (customize as needed)
            for col in ["Category", "Location", "Date", "Item Purchased", "Open", "Close", "Volume"]:
                if col in row:
                    meta[col] = str(row[col])
        metadatas.append(meta)
    # Build vector DB
    vector_db = VectorDB(persist_path=persist_path)
    vector_db.add_documents(embeddings, metadatas)
    print(f"RAG index built with {vector_db.num_documents()} documents.")
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
    print(f"Querying for context: '{query}'")
    query_embedding = embed_texts([query], embedding_model)[0]
    results = vector_db.query(query_embedding, top_k=top_k)
    print(f"Retrieved {len(results)} context chunks.")
    if results:
        print(f"First retrieved chunk text: {results[0].get('text', 'N/A')[:100]}...")
    return results 