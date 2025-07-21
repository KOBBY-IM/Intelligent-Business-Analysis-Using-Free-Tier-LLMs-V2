import json
import os
from datetime import datetime, timedelta
import random

def create_sample_blind_data():
    """Create sample blind evaluation data for testing the analysis dashboard"""
    
    # Sample data
    llm_models = [
        "groq/llama3-70b-8192",
        "groq/moonshotai/kimi-k2-instruct", 
        "openrouter/mistralai/mistral-7b-instruct",
        "openrouter/deepseek/deepseek-r1-0528-qwen3-8b"
    ]
    
    industries = ["retail", "finance"]
    questions = [
        "What are the key trends in customer purchasing behavior?",
        "How can we optimize inventory management?",
        "What factors influence stock price volatility?",
        "How should we approach risk management?"
    ]
    
    evaluators = [
        {"name": "Dr. Sarah Johnson", "email": "sarah.johnson@business.edu"},
        {"name": "Prof. Michael Chen", "email": "michael.chen@analytics.edu"},
        {"name": "Dr. Emily Rodriguez", "email": "emily.rodriguez@research.edu"},
        {"name": "Prof. David Kim", "email": "david.kim@data.edu"},
        {"name": "Dr. Lisa Wang", "email": "lisa.wang@business.edu"}
    ]
    
    data = []
    
    # Generate evaluations over the past week
    start_date = datetime.now() - timedelta(days=7)
    
    for day in range(7):
        for eval_num in range(random.randint(3, 8)):  # 3-8 evaluations per day
            evaluator = random.choice(evaluators)
            llm = random.choice(llm_models)
            industry = random.choice(industries)
            question = random.choice(questions)
            
            # Generate timestamp
            timestamp = start_date + timedelta(
                days=day,
                hours=random.randint(9, 17),  # Business hours
                minutes=random.randint(0, 59)
            )
            
            # Generate realistic ratings (1-5 scale)
            quality = random.randint(3, 5) + random.random() * 0.5
            relevance = random.randint(3, 5) + random.random() * 0.5
            accuracy = random.randint(3, 5) + random.random() * 0.5
            uniformity = random.randint(3, 5) + random.random() * 0.5
            
            # Generate sample comments
            comments = [
                "Very comprehensive analysis with good insights.",
                "Response was relevant but could be more detailed.",
                "Excellent accuracy in addressing the business question.",
                "Good quality response with practical recommendations.",
                "Well-structured answer with clear explanations.",
                "Response shows good understanding of the industry context.",
                "Accurate data interpretation and logical conclusions.",
                "Consistent quality throughout the response."
            ]
            
            evaluation = {
                "timestamp": timestamp.isoformat(),
                "evaluator_name": evaluator["name"],
                "evaluator_email": evaluator["email"],
                "llm_model": llm,
                "current_industry": industry,
                "question": question,
                "quality": round(quality, 1),
                "relevance": round(relevance, 1),
                "accuracy": round(accuracy, 1),
                "uniformity": round(uniformity, 1),
                "comments": random.choice(comments),
                "consent_given": True,
                "evaluation_id": f"eval_{day}_{eval_num}_{hash(llm) % 1000}"
            }
            
            data.append(evaluation)
    
    # Save to JSON
    output_path = os.path.join('data', 'sample_evaluations.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Created sample blind evaluation data with {len(data)} records")
    print(f"📁 Saved to: {output_path}")
    print(f"📊 Data spans: {data[0]['timestamp']} to {data[-1]['timestamp']}")
    print(f"👥 Evaluators: {len(evaluators)}")
    print(f"🤖 LLM Models: {len(llm_models)}")
    print(f"🏭 Industries: {len(industries)}")
    
    return data

if __name__ == "__main__":
    create_sample_blind_data() 