"""
chunking.py
Module for splitting text into retrievable chunks for RAG.
"""
from typing import List

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split a long text into overlapping chunks.
    Args:
        text: The input text
        chunk_size: Number of characters per chunk
        overlap: Number of overlapping characters between chunks
    Returns:
        List of text chunks
    """
    if not text:
        return []
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == text_length:
            break
        start += chunk_size - overlap
    return chunks

def chunk_documents(docs: List[str], chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Chunk a list of documents into retrievable chunks.
    Args:
        docs: List of text documents
        chunk_size: Number of characters per chunk
        overlap: Number of overlapping characters between chunks
    Returns:
        List of all text chunks
    """
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_text(doc, chunk_size=chunk_size, overlap=overlap))
    return all_chunks 