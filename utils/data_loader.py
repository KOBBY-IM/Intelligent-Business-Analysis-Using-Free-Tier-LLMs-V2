"""
data_loader.py
Module for loading and parsing datasets (CSV, TXT) for RAG pipeline.
"""
import pandas as pd
from typing import List, Optional
import os

def load_csv_dataset(path: str, text_column: Optional[str] = None) -> List[str]:
    """
    Load a CSV dataset and return a list of text documents.
    Args:
        path: Path to the CSV file
        text_column: Optional column name to use as text. If None, use first column.
    Returns:
        List of text documents
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the specified column does not exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV file not found: {path}")
    df = pd.read_csv(path)
    if text_column is None:
        text_column = df.columns[0]
    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in CSV.")
    docs = df[text_column].dropna().astype(str).tolist()
    return docs

def load_text_dataset(path: str) -> List[str]:
    """
    Load a plain text dataset (one document per line or full text).
    Args:
        path: Path to the text file
    Returns:
        List of text documents (one per line, or single doc if no newlines)
    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Text file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    # If only one line, treat as single document
    if len(lines) == 1:
        return lines
    return lines 