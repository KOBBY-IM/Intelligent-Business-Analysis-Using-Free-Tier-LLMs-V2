"""
prompts.py
Module for constructing LLM prompts with retrieved context.
"""
from typing import List, Dict, Any

def build_prompt(question: str, context_chunks: List[Any]) -> str:
    """
    Build a prompt for LLM with context chunks.
    Args:
        question: The business analysis question
        context_chunks: List of context chunks (can be strings or dicts with 'text' key)
    Returns:
        Formatted prompt string
    """
    # Extract text from context chunks
    context_texts = []
    for i, chunk in enumerate(context_chunks):
        if isinstance(chunk, dict):
            text = chunk.get('text', str(chunk))
        else:
            text = str(chunk)
        context_texts.append(text)
    
    # Join all context into a single block
    context_block = "\n\n".join(context_texts)
    
    prompt = f"""You are a business analysis assistant. Use ONLY the following context to answer the question. If the answer is not in the context, say 'Not found in provided data.'

Context:
{context_block}

Question: {question}

Instructions:
1. Provide a clear, concise answer based on the context data
2. Include relevant business insights and implications
3. Use specific numbers and data points when available
4. Explain what the data means for business decision-making
5. Do not cite specific chunks or sources - focus on the business analysis
6. If the context contains summary statistics, use them to support your analysis

Answer:"""
    
    return prompt 