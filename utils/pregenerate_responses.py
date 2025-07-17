"""
pregenerate_responses.py
Script to pregenerate LLM responses for all evaluation questions using the RAG pipeline.
"""
import json
from typing import List, Dict
from utils.rag_pipeline import build_rag_index, retrieve_context
from utils.llm_clients import get_llm_client
from utils.prompts import build_prompt
import os
import time

def load_questions(path: str) -> Dict[str, List[str]]:
    """
    Load evaluation questions from a JSON file.
    Args:
        path: Path to eval_questions.json
    Returns:
        Dict with industry as key and list of questions as value
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Paths
    questions_path = os.path.join('data', 'eval_questions.json')
    output_path = os.path.join('data', 'pregenerated_responses.json')
    # Map industry to dataset path
    industry_to_dataset = {
        "retail": "data/shopping_trends.csv",
        "finance": "data/Tesla_stock_data.csv"
    }
    # Load questions
    questions = load_questions(questions_path)
    # Define LLMs to use (provider, model)
    llms = [
        {"provider": "groq", "model": "groq-llm-model"},
        {"provider": "gemini", "model": "gemini-pro"},
        {"provider": "openrouter", "model": "openrouter-llm-model-1"},
        {"provider": "openrouter", "model": "openrouter-llm-model-2"}
    ]
    # Build RAG index for each industry (cache for reuse)
    rag_indices = {}
    embedding_models = {}
    for industry, dataset_path in industry_to_dataset.items():
        print(f"Building RAG index for {industry} ({dataset_path})...")
        rag_indices[industry] = build_rag_index(dataset_path, dataset_type="csv")
        from utils.embedding import get_embedding_model
        embedding_models[industry] = get_embedding_model()
    # For each industry and question, run RAG and call each LLM
    all_results = []
    for industry, qs in questions.items():
        rag_index = rag_indices[industry]
        embedding_model = embedding_models[industry]
        for q in qs:
            print(f"\n[Industry: {industry}] Question: {q}")
            # Retrieve context using RAG
            try:
                context_results = retrieve_context(q, rag_index, embedding_model, top_k=3)
                context_chunks = [r["text"] for r in context_results]
            except Exception as e:
                print(f"  Error retrieving context: {e}")
                context_chunks = []
            # Build prompt
            prompt = build_prompt(q, context_chunks)
            # Call each LLM
            for llm in llms:
                print(f"  Calling {llm['provider']} ({llm['model']})...")
                client = get_llm_client(llm["provider"], llm["model"])
                try:
                    response = client.generate(prompt)
                    error = None
                except Exception as e:
                    response = ""
                    error = str(e)
                    print(f"    Error: {error}")
                result = {
                    "industry": industry,
                    "question": q,
                    "llm_provider": llm["provider"],
                    "llm_model": llm["model"],
                    "context": context_chunks,
                    "prompt": prompt,
                    "response": response,
                    "error": error,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                all_results.append(result)
                # Optional: Sleep to respect rate limits
                time.sleep(1)
    # Save all results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nPregenerated responses saved to {output_path}")

if __name__ == "__main__":
    main() 