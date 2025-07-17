"""
prompts.py
Module for constructing LLM prompts with retrieved context.
"""
from typing import List

def build_prompt(query: str, context_chunks: List[str]) -> str:
    """
    Build a prompt for the LLM using the query and retrieved context.
    Args:
        query: The user/business query
        context_chunks: List of retrieved context strings
    Returns:
        Prompt string for LLM
    """
    context = "\n---\n".join(context_chunks)
    prompt = f"You are a business analysis assistant. Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    return prompt 