"""
vector_db.py
Module for storing and retrieving embeddings using a vector database (ChromaDB/FAISS).
"""
from typing import List, Any, Dict
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np

class VectorDB:
    """
    Abstracts vector database operations for RAG using ChromaDB (client-only mode).
    """
    def __init__(self, persist_path: str = None):
        """
        Initialize the vector database (in-memory or file-based).
        Args:
            persist_path: Optional path for persistence
        """
        self.persist_path = persist_path
        if persist_path:
            self.client = chromadb.Client(Settings(
                persist_directory=persist_path,
                is_persistent=True
            ))
        else:
            self.client = chromadb.Client(Settings(
                is_persistent=False
            ))
        self.collection = self.client.create_collection("rag_collection")

    def add_documents(self, embeddings: List[list], metadatas: List[dict]):
        """
        Add documents (embeddings + metadata) to the vector DB.
        Args:
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts (e.g., chunk text, doc id)
        """
        ids = [str(i) for i in range(len(embeddings))]
        self.collection.add(
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_embedding: list, top_k: int = 5) -> List[Dict]:
        """
        Query the vector DB for the most similar chunks.
        Args:
            query_embedding: Embedding vector for the query
            top_k: Number of top results to return
        Returns:
            List of metadata dicts for top results
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        # Return metadata for top results
        return [meta for meta in results["metadatas"][0]] 