import os
import json
import time
import csv
from datetime import datetime
from typing import List, Dict, Any

# --- BEGIN: Streamlit secrets GCS credential support ---
def setup_gcs_credentials():
    """Set up GCS credentials from various sources"""
    try:
        # First try: Check if already set via environment variables
        if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            print("[INFO] Using existing GOOGLE_APPLICATION_CREDENTIALS from environment")
            return True
            
        # Second try: Streamlit context (if available)
        try:
            import streamlit as st
            service_account_info = None
            bucket_name = None
            
            # Check for gcp_service_account format
            if "gcp_service_account" in st.secrets:
                print("[INFO] Found GCP credentials in Streamlit secrets (gcp_service_account)")
                service_account_info = st.secrets["gcp_service_account"]
                bucket_name = st.secrets.get("gcs_bucket_name")
            # Check for gcs.service_account format
            elif "gcs" in st.secrets and "service_account" in st.secrets["gcs"]:
                print("[INFO] Found GCP credentials in Streamlit secrets (gcs.service_account)")
                service_account_info = st.secrets["gcs"]["service_account"]
                bucket_name = st.secrets["gcs"].get("bucket_name")
            
            if service_account_info:
                if isinstance(service_account_info, str):
                    service_account_info = json.loads(service_account_info)
                import tempfile
                with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
                    json.dump(service_account_info, f)
                    temp_cred_path = f.name
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_cred_path
                if bucket_name:
                    os.environ["GCS_BUCKET"] = bucket_name
                print(f"[INFO] Created temporary credentials file: {temp_cred_path}")
                return True
        except ImportError:
            pass  # Not in Streamlit context
        except Exception as e:
            print(f"[WARN] Could not use Streamlit secrets: {e}")
            
        # Third try: Read secrets.toml directly (for local development)
        secrets_path = ".streamlit/secrets.toml"
        if os.path.exists(secrets_path):
            print("[INFO] Reading credentials from .streamlit/secrets.toml")
            try:
                import toml
                secrets = toml.load(secrets_path)
                
                service_account_info = None
                bucket_name = None
                
                # Check for gcp_service_account format
                if "gcp_service_account" in secrets:
                    service_account_info = secrets["gcp_service_account"]
                    bucket_name = secrets.get("gcs_bucket_name")
                # Check for gcs.service_account format  
                elif "gcs" in secrets and "service_account" in secrets["gcs"]:
                    service_account_info = secrets["gcs"]["service_account"]
                    bucket_name = secrets["gcs"].get("bucket_name")
                
                if service_account_info:
                    # Handle string format (your case)
                    if isinstance(service_account_info, str):
                        service_account_info = json.loads(service_account_info)
                    
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
                        json.dump(service_account_info, f)
                        temp_cred_path = f.name
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_cred_path
                    
                    # Set bucket name if available
                    if bucket_name:
                        os.environ["GCS_BUCKET"] = bucket_name
                    
                    print(f"[INFO] Created credentials from secrets.toml: {temp_cred_path}")
                    print(f"[INFO] Using bucket: {bucket_name or 'llm-evaluation-data (default)'}")
                    return True
                else:
                    print("[WARN] No GCP service account found in secrets.toml")
                    
            except ImportError:
                print("[WARN] toml package not found. Install with: pip install toml")
            except Exception as e:
                print(f"[WARN] Error reading secrets.toml: {e}")
        
        print("[WARN] No GCP credentials found. GCS upload will be skipped.")
        return False
        
    except Exception as e:
        print(f"[ERROR] Error setting up GCS credentials: {e}")
        return False

# Set up credentials at startup
setup_gcs_credentials()
# --- END: Streamlit secrets GCS credential support ---

from utils.rag_pipeline import build_rag_index, retrieve_context
from utils.llm_clients import get_llm_client
from utils.prompts import build_prompt
from utils.embedding import get_embedding_model, embed_texts
from utils.vector_db import VectorDB
from utils.data_loader import load_csv_dataset, load_text_dataset
from utils.chunking import chunk_documents
from google.cloud import storage

# ---- CONFIGURATION ----
# Paths
QUESTIONS_PATH = os.path.join('data', 'eval_questions.json')
INDUSTRY_TO_DATASET = {
    "retail": "data/shopping_trends.csv",
    "finance": "data/Tesla_stock_data.csv"
}
OUTPUT_JSON = os.path.join('data', 'batch_eval_metrics.json')
OUTPUT_CSV = os.path.join('data', 'batch_eval_metrics.csv')
GCS_BUCKET = os.environ.get('GCS_BUCKET', 'llm-evaluation-data')
GCS_JSON_BLOB = 'batch_eval_metrics.json'
GCS_CSV_BLOB = 'batch_eval_metrics.csv'
GCP_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')  # Path to service account JSON

# LLMs to evaluate
LLMS = [
    {"provider": "groq", "model": "llama3-70b-8192"},
    {"provider": "groq", "model": "moonshotai/kimi-k2-instruct"},
    {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct"},
    {"provider": "openrouter", "model": "deepseek/deepseek-r1-0528-qwen3-8b"},
]

# ---- UTILS ----
def load_questions(path: str) -> Dict[str, List[str]]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def count_tokens(text: str) -> int:
    # Approximate: use whitespace word count as token proxy
    return len(text.split())

def upload_to_gcs(local_path: str, bucket_name: str, blob_name: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    print(f"Uploaded {local_path} to gs://{bucket_name}/{blob_name}")

def save_json(data: List[Dict[str, Any]], path: str):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def save_csv(data: List[Dict[str, Any]], path: str):
    if not data:
        return
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)

def compute_coverage(answer: str, context_chunks: list) -> float:
    """Compute the fraction of answer words that appear in the context."""
    import re
    answer_words = set(re.findall(r"\w+", answer.lower()))
    context_text = " ".join(context_chunks).lower()
    context_words = set(re.findall(r"\w+", context_text))
    if not answer_words:
        return 0.0
    overlap = answer_words & context_words
    return len(overlap) / len(answer_words)

def build_rag_index_with_collection(dataset_path: str, collection_name: str, dataset_type: str = "csv", text_column: str = None, chunk_size: int = 500, overlap: int = 50, persist_path: str = None) -> VectorDB:
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
    # Build vector DB with unique collection name
    vector_db = VectorDB(collection_name=collection_name, persist_path=persist_path)
    vector_db.add_documents(embeddings, metadatas)
    return vector_db

# ---- MAIN BATCH EVALUATION ----
def main():
    # Load questions
    questions = load_questions(QUESTIONS_PATH)
    # Build RAG index and embedding model for each industry
    rag_indices = {}
    embedding_models = {}
    for industry, dataset_path in INDUSTRY_TO_DATASET.items():
        print(f"Building RAG index for {industry} ({dataset_path})...")
        collection_name = f"rag_collection_{industry}"
        rag_indices[industry] = build_rag_index_with_collection(dataset_path, collection_name, dataset_type="csv")
        embedding_models[industry] = get_embedding_model()
    # --- Select 5 random questions across all industries ---
    import random
    all_questions = []
    for industry, qs in questions.items():
        for q in qs:
            all_questions.append((industry, q))
    selected = random.sample(all_questions, min(5, len(all_questions)))
    # Main evaluation loop
    all_metrics = []
    batch_timestamp = datetime.utcnow().isoformat() + 'Z'
    for industry, q in selected:
        rag_index = rag_indices[industry]
        embedding_model = embedding_models[industry]
        # Retrieve context
        try:
            context_results = retrieve_context(q, rag_index, embedding_model, top_k=3)
            context_chunks = [r["text"] for r in context_results]
        except Exception as e:
            print(f"[ERROR] Context retrieval failed: {e}")
            context_chunks = []
        prompt = build_prompt(q, context_chunks)
        prompt_tokens = count_tokens(prompt)
        for llm in LLMS:
            client = get_llm_client(llm["provider"], llm["model"])
            retry_count = 0
            max_retries = 3
            latency = None
            response = ""
            response_tokens = 0
            total_tokens = prompt_tokens
            throughput = 0
            success = False
            error = None
            rate_limit_hit = False
            error_type = None
            while retry_count < max_retries:
                start = time.time()
                try:
                    response = client.generate(prompt)
                    latency = time.time() - start
                    response_tokens = count_tokens(response)
                    total_tokens = prompt_tokens + response_tokens
                    throughput = response_tokens / latency if latency > 0 else 0
                    success = True
                    error = None
                    rate_limit_hit = False
                    error_type = None
                    break
                except Exception as e:
                    latency = None
                    response = ""
                    response_tokens = 0
                    total_tokens = prompt_tokens
                    throughput = 0
                    success = False
                    error = str(e)
                    # Error parsing for type and rate limit
                    err_str = str(e).lower()
                    if any(x in err_str for x in ["rate limit", "too many requests", "429"]):
                        rate_limit_hit = True
                        error_type = "rate_limit"
                    elif any(x in err_str for x in ["timeout", "timed out"]):
                        error_type = "timeout"
                    elif any(x in err_str for x in ["network", "connection"]):
                        error_type = "network"
                    elif any(x in err_str for x in ["api", "invalid request", "bad request"]):
                        error_type = "api_error"
                    else:
                        error_type = "other"
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(2)  # brief pause before retry
            coverage_score = compute_coverage(response, context_chunks)
            metric = {
                "timestamp": batch_timestamp,
                "industry": industry,
                "question": q,
                "llm_provider": llm["provider"],
                "llm_model": llm["model"],
                "latency_sec": latency,
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens,
                "total_tokens": total_tokens,
                "throughput_tps": throughput,
                "success": success,
                "error": error,
                "coverage_score": coverage_score,
                "retry_count": retry_count,
                "rate_limit_hit": rate_limit_hit,
                "error_type": error_type,
            }
            all_metrics.append(metric)
            latency_str = f"{latency:.2f}s" if latency is not None else "N/A"
            coverage_str = f"{coverage_score:.2f}" if coverage_score is not None else "N/A"
            print(f"[{industry}] {llm['provider']}:{llm['model']} | Latency: {latency_str} | Success: {success} | Coverage: {coverage_str} | Retries: {retry_count} | RateLimit: {rate_limit_hit} | ErrorType: {error_type}")
    # Save results
    save_json(all_metrics, OUTPUT_JSON)
    save_csv(all_metrics, OUTPUT_CSV)
    # Upload to GCS
    if GCP_CREDENTIALS:
        upload_to_gcs(OUTPUT_JSON, GCS_BUCKET, GCS_JSON_BLOB)
        upload_to_gcs(OUTPUT_CSV, GCS_BUCKET, GCS_CSV_BLOB)
    else:
        print("GCP credentials not set. Skipping GCS upload.")
    print(f"Batch evaluation complete. {len(all_metrics)} records saved.")

if __name__ == "__main__":
    main() 