import json
import csv
import random
from datetime import datetime, timedelta
import os

# Config
industries = ["retail", "finance"]
llm_models = ["groq-llm-model", "gemini-pro", "openrouter-llm-model-1", "openrouter-llm-model-2"]
comments = [
    "Very relevant answer.", "Somewhat generic.", "Accurate and concise.", "Missed some details.",
    "Great coverage of context.", "Could be more specific.", "Excellent explanation.", "Too verbose."
]

# Generate random human evaluation data
def generate_evaluations(num_records=40):
    data = []
    now = datetime.utcnow()
    for _ in range(num_records):
        industry = random.choice(industries)
        llm = random.choice(llm_models)
        record = {
            "current_industry": industry,
            "llm_model": llm,
            "quality": random.randint(1, 5),
            "relevance": random.randint(1, 5),
            "accuracy": random.randint(1, 5),
            "uniformity": random.randint(1, 5),
            "comments": random.choice(comments) if random.random() < 0.7 else "",
            "evaluation_timestamp": (now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        data.append(record)
    return data

# Generate random technical metrics data
def generate_tech_metrics(num_records=40):
    data = []
    now = datetime.utcnow()
    for _ in range(num_records):
        industry = random.choice(industries)
        llm = random.choice(llm_models)
        latency = round(random.uniform(0.8, 2.5), 2)
        throughput = round(random.uniform(20, 40), 2)
        success = random.choice([1, 1, 1, 0])  # 75% success
        coverage = round(random.uniform(0.4, 0.9), 2)
        timestamp = (now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))).strftime("%Y-%m-%dT%H:%M:%SZ")
        data.append({
            "industry": industry,
            "llm_model": llm,
            "latency_sec": latency,
            "throughput_tps": throughput,
            "success": success,
            "coverage_score": coverage,
            "timestamp": timestamp
        })
    return data

# Write to files
def main():
    os.makedirs("data", exist_ok=True)
    evals = generate_evaluations(40)
    with open("data/evaluations.json", "w", encoding="utf-8") as f:
        json.dump(evals, f, indent=2)
    tech = generate_tech_metrics(40)
    with open("data/batch_eval_metrics.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(tech[0].keys()))
        writer.writeheader()
        writer.writerows(tech)
    print("Sample data generated: data/evaluations.json, data/batch_eval_metrics.csv")

if __name__ == "__main__":
    main() 