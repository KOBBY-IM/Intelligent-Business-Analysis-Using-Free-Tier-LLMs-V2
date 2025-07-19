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
import pandas as pd

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

def compute_retail_summary(question, df):
    q = question.lower()
    if "highest total sales" in q or "most revenue" in q:
        # Top categories by total revenue
        summary = df.groupby('Category')['Purchase Amount (USD)'].sum().sort_values(ascending=False)
        return f"Summary: Total revenue by category: {', '.join([f'{cat}: ${val:.2f}' for cat, val in summary.items()])}"
    if "average sales" in q:
        avg = df.groupby('Category')['Purchase Amount (USD)'].mean()
        return f"Summary: Average purchase amount per category: {', '.join([f'{cat}: ${val:.2f}' for cat, val in avg.items()])}"
    if "best-selling product" in q:
        best = df.groupby('Location').apply(lambda x: x.loc[x['Purchase Amount (USD)'].idxmax()]['Item Purchased'])
        return f"Summary: Best-selling product by location: {', '.join([f'{loc}: {prod}' for loc, prod in best.items()])}"
    if "review rating" in q:
        avg_rating = df.groupby('Category')['Review Rating'].mean()
        return f"Summary: Average review rating by category: {', '.join([f'{cat}: {val:.2f}' for cat, val in avg_rating.items()])}"
    if "payment method" in q:
        top_method = df['Payment Method'].mode()[0]
        return f"Summary: Most popular payment method: {top_method}"
    if "shipping type" in q:
        top_ship = df['Shipping Type'].mode()[0]
        return f"Summary: Most popular shipping type: {top_ship}"
    if "discount" in q or "promo code" in q:
        discount_rate = (df['Discount Applied'].str.lower() == 'yes').mean() * 100
        promo_rate = (df['Promo Code Used'].str.lower() == 'yes').mean() * 100
        return f"Summary: Discount applied in {discount_rate:.1f}% of purchases, promo code used in {promo_rate:.1f}% of purchases."
    if "frequency" in q:
        freq = df['Frequency of Purchases'].mode()[0]
        return f"Summary: Most common purchase frequency: {freq}"
    return None

def compute_finance_summary(question, df):
    q = question.lower()
    if "highest closing price" in q:
        row = df.loc[df['Close'].idxmax()]
        return f"Summary: Highest closing price: {row['Close']} on {row['Date']}"
    if "largest single-day price increase" in q:
        df['change'] = df['Close'] - df['Open']
        row = df.loc[df['change'].idxmax()]
        return f"Summary: Largest single-day price increase: {row['change']} on {row['Date']}"
    if "average daily trading volume" in q:
        avg = df['Volume'].mean()
        return f"Summary: Average daily trading volume: {avg:.2f}"
    if "overall percentage change" in q:
        pct = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
        return f"Summary: Overall percentage change in closing price: {pct:.2f}%"
    return None

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
    # Load dataframes for summary stats
    retail_df = pd.read_csv(industry_to_dataset['retail'])
    finance_df = pd.read_csv(industry_to_dataset['finance'])

    # Create RAG_Text column for retail
    retail_df["RAG_Text"] = (
        "Customer: " + retail_df["Customer ID"].astype(str) +
        ", Age: " + retail_df["Age"].astype(str) +
        ", Gender: " + retail_df["Gender"] +
        ", Item: " + retail_df["Item Purchased"] +
        ", Category: " + retail_df["Category"] +
        ", Amount: $" + retail_df["Purchase Amount (USD)"].astype(str) +
        ", Location: " + retail_df["Location"] +
        ", Review: " + retail_df["Review Rating"].astype(str) +
        ", Payment: " + retail_df["Payment Method"] +
        ", Shipping: " + retail_df["Shipping Type"] +
        ", Discount: " + retail_df["Discount Applied"] +
        ", Promo: " + retail_df["Promo Code Used"] +
        ", Frequency: " + retail_df["Frequency of Purchases"]
    )
    retail_df.to_csv("data/shopping_trends_with_rag.csv", index=False)

    # Create RAG_Text column for finance
    finance_df["RAG_Text"] = (
        "Date: " + finance_df["Date"].astype(str) +
        ", Open: " + finance_df["Open"].astype(str) +
        ", Close: " + finance_df["Close"].astype(str) +
        ", High: " + finance_df["High"].astype(str) +
        ", Low: " + finance_df["Low"].astype(str) +
        ", Volume: " + finance_df["Volume"].astype(str)
    )
    finance_df.to_csv("data/Tesla_stock_data_with_rag.csv", index=False)

    # Define LLMs to use (provider, model)
    llms = [
        {"provider": "groq", "model": "llama3-70b-8192"},
        {"provider": "groq", "model": "moonshotai/kimi-k2-instruct"},
        {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct"},
        {"provider": "openrouter", "model": "deepseek/deepseek-r1-0528-qwen3-8b"}
    ]
    # Build RAG index for each industry (cache for reuse)
    rag_indices = {}
    embedding_models = {}
    rag_index_paths = {
        "retail": "data/shopping_trends_with_rag.csv",
        "finance": "data/Tesla_stock_data_with_rag.csv"
    }
    for industry, dataset_path in rag_index_paths.items():
        print(f"Building RAG index for {industry} ({dataset_path})...")
        rag_indices[industry] = build_rag_index(dataset_path, dataset_type="csv", text_column="RAG_Text")
        from utils.embedding import get_embedding_model
        embedding_models[industry] = get_embedding_model()
    # For each industry and question, run RAG and call each LLM
    all_results = []
    for industry, qs in questions.items():
        rag_index = rag_indices[industry]
        embedding_model = embedding_models[industry]
        # Select the right dataframe and summary function
        if industry == 'retail':
            df = retail_df
            summary_func = compute_retail_summary
        else:
            df = finance_df
            summary_func = compute_finance_summary
        for q in qs:
            print(f"\n[Industry: {industry}] Question: {q}")
            # Retrieve top 5 context chunks using RAG
            try:
                context_results = retrieve_context(q, rag_index, embedding_model, top_k=5)
                context_chunks = context_results  # Pass full dicts for prompt metadata
                print(f"  Context_chunks from retrieve_context (length {len(context_chunks)}): {context_chunks}")
            except Exception as e:
                print(f"  Error retrieving context: {e}")
                context_chunks = []
            # Compute summary if relevant
            summary = summary_func(q, df)
            if summary:
                context_chunks = [summary] + context_chunks
                print(f"  Summary added. New context_chunks length: {len(context_chunks)}. First item type: {type(context_chunks[0])}")
            # Build prompt
            prompt = build_prompt(q, context_chunks)
            print(f"  Prompt built (first 500 chars): {prompt[:500]}...")
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