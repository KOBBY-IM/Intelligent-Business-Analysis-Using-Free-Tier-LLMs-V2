import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_sample_batch_data():
    """Create sample batch evaluation metrics data for testing the analysis dashboard"""
    
    # Sample LLM models
    llm_models = [
        "groq/llama3-70b-8192",
        "groq/moonshotai/kimi-k2-instruct", 
        "openrouter/mistralai/mistral-7b-instruct",
        "openrouter/deepseek/deepseek-r1-0528-qwen3-8b"
    ]
    
    # Sample industries
    industries = ["retail", "finance"]
    
    # Generate 4 days of data with 14 evaluations per 12-hour period
    start_date = datetime.now() - timedelta(days=4)
    data = []
    
    for day in range(4):
        for period in range(2):  # 2 periods per day (12 hours each)
            for eval_num in range(14):  # 14 evaluations per period
                for llm in llm_models:
                    for industry in industries:
                        # Generate timestamp
                        timestamp = start_date + timedelta(
                            days=day,
                            hours=period * 12 + eval_num * 0.85,  # Spread evaluations across 12 hours
                            minutes=np.random.randint(0, 60)
                        )
                        
                        # Generate realistic metrics
                        latency = np.random.normal(2.5, 0.8)  # 2.5s average, 0.8s std
                        throughput = np.random.normal(150, 30)  # 150 tokens/sec average
                        success = np.random.choice([0, 1], p=[0.05, 0.95])  # 95% success rate
                        coverage = np.random.normal(0.75, 0.1)  # 75% coverage average
                        
                        # Ensure realistic bounds
                        latency = max(0.5, min(10, latency))
                        throughput = max(50, min(300, throughput))
                        coverage = max(0.3, min(1.0, coverage))
                        
                        data.append({
                            'timestamp': timestamp.isoformat(),
                            'llm_model': llm,
                            'industry': industry,
                            'latency_sec': round(latency, 3),
                            'throughput_tps': round(throughput, 1),
                            'success': success,
                            'coverage_score': round(coverage, 3),
                            'tokens_generated': np.random.randint(50, 500),
                            'context_tokens': np.random.randint(100, 1000),
                            'response_quality': np.random.randint(1, 6),
                            'error_message': None if success else "API timeout"
                        })
    
    # Create DataFrame and save
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_path = os.path.join('data', 'batch_eval_metrics.csv')
    df.to_csv(output_path, index=False)
    
    print(f"✅ Created sample batch evaluation data with {len(df)} records")
    print(f"📁 Saved to: {output_path}")
    print(f"📊 Data spans: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"🤖 LLM Models: {df['llm_model'].nunique()}")
    print(f"🏭 Industries: {df['industry'].nunique()}")
    
    return df

if __name__ == "__main__":
    create_sample_batch_data() 