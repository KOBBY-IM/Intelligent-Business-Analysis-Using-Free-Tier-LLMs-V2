#!/usr/bin/env python3
"""
Analysis of the current random question selection approach for blind evaluations
"""

import json
import random
import pandas as pd
from typing import List, Dict, Tuple
from collections import Counter

def analyze_current_random_selection():
    """Analyze the current random question selection implementation"""
    
    print("🎲 RANDOM QUESTION SELECTION ANALYSIS")
    print("=" * 60)
    
    # Load current questions
    with open('data/eval_questions.json', 'r') as f:
        questions = json.load(f)
    
    # Load evaluation data
    try:
        with open('data/evaluations.json', 'r') as f:
            evaluations = json.load(f)
    except:
        evaluations = []
    
    print(f"\n📊 CURRENT IMPLEMENTATION:")
    print(f"   Total Questions Available: 20 (10 retail + 10 finance)")
    print(f"   Questions Per Tester: 12 (6 retail + 6 finance)")
    print(f"   Selection Method: Random sampling")
    print(f"   Coverage: 60% of available questions per tester")
    
    # Analyze question distribution
    print(f"\n🎯 QUESTION DISTRIBUTION ANALYSIS:")
    
    retail_questions = questions['retail']
    finance_questions = questions['finance']
    
    print(f"\n   Retail Questions (10 total):")
    for i, q in enumerate(retail_questions, 1):
        question_type = "Revenue" if "revenue" in q.lower() else "Transaction" if "transaction" in q.lower() else "Sales" if "sales" in q.lower() else "Product" if "product" in q.lower() else "Regional" if "region" in q.lower() else "Other"
        print(f"     {i}. {question_type}: {q[:50]}...")
    
    print(f"\n   Finance Questions (10 total):")
    for i, q in enumerate(finance_questions, 1):
        question_type = "Price" if "price" in q.lower() else "Volume" if "volume" in q.lower() else "Trend" if "trend" in q.lower() else "Volatility" if "volatility" in q.lower() else "Correlation" if "correlation" in q.lower() else "Other"
        print(f"     {i}. {question_type}: {q[:50]}...")
    
    return questions, evaluations

def simulate_random_selection_impact():
    """Simulate the impact of random selection on question coverage"""
    
    print(f"\n🎲 RANDOM SELECTION SIMULATION:")
    print("=" * 40)
    
    # Simulate multiple testers with random selection
    num_simulations = 1000
    num_testers = 20
    
    retail_questions = list(range(10))  # 0-9 for retail questions
    finance_questions = list(range(10))  # 0-9 for finance questions
    
    # Track question selection frequency
    retail_selection_count = Counter()
    finance_selection_count = Counter()
    
    # Track coverage patterns
    coverage_patterns = []
    
    for simulation in range(num_simulations):
        # Simulate testers
        for tester in range(num_testers):
            # Random selection: 6 retail + 6 finance
            selected_retail = random.sample(retail_questions, 6)
            selected_finance = random.sample(finance_questions, 6)
            
            # Count selections
            for q in selected_retail:
                retail_selection_count[q] += 1
            for q in selected_finance:
                finance_selection_count[q] += 1
            
            # Track coverage pattern
            coverage_patterns.append({
                'retail_coverage': len(set(selected_retail)),
                'finance_coverage': len(set(selected_finance)),
                'total_coverage': len(set(selected_retail + selected_finance))
            })
    
    print(f"   Simulations: {num_simulations} runs with {num_testers} testers each")
    print(f"   Total Evaluations Simulated: {num_simulations * num_testers:,}")
    
    # Analyze selection frequency
    print(f"\n   📊 QUESTION SELECTION FREQUENCY:")
    
    print(f"\n   Retail Questions Selection Rate:")
    for i in range(10):
        selection_rate = (retail_selection_count[i] / (num_simulations * num_testers)) * 100
        print(f"     Question {i+1}: {selection_rate:.1f}%")
    
    print(f"\n   Finance Questions Selection Rate:")
    for i in range(10):
        selection_rate = (finance_selection_count[i] / (num_simulations * num_testers)) * 100
        print(f"     Question {i+1}: {selection_rate:.1f}%")
    
    # Analyze coverage patterns
    avg_retail_coverage = sum(p['retail_coverage'] for p in coverage_patterns) / len(coverage_patterns)
    avg_finance_coverage = sum(p['finance_coverage'] for p in coverage_patterns) / len(coverage_patterns)
    avg_total_coverage = sum(p['total_coverage'] for p in coverage_patterns) / len(coverage_patterns)
    
    print(f"\n   📈 COVERAGE ANALYSIS:")
    print(f"     Average Retail Coverage: {avg_retail_coverage:.1f}/6 questions")
    print(f"     Average Finance Coverage: {avg_finance_coverage:.1f}/6 questions")
    print(f"     Average Total Coverage: {avg_total_coverage:.1f}/12 questions")
    
    return retail_selection_count, finance_selection_count

def analyze_data_collection_impact():
    """Analyze impact on data collection and analysis"""
    
    print(f"\n📊 DATA COLLECTION IMPACT:")
    print("=" * 40)
    
    # Current setup analysis
    total_questions = 20
    questions_per_tester = 12
    llms_per_question = 4
    
    print(f"   Current Setup:")
    print(f"     Total Questions Available: {total_questions}")
    print(f"     Questions Per Tester: {questions_per_tester}")
    print(f"     Evaluations Per Tester: {questions_per_tester * llms_per_question}")
    print(f"     Coverage Per Tester: {(questions_per_tester/total_questions)*100:.0f}%")
    
    # Statistical power analysis
    print(f"\n   📈 STATISTICAL POWER:")
    evaluations_per_llm_per_tester = questions_per_tester
    print(f"     Evaluations per LLM per Tester: {evaluations_per_llm_per_tester}")
    
    if evaluations_per_llm_per_tester >= 10:
        power_assessment = "Good statistical power"
    elif evaluations_per_llm_per_tester >= 6:
        power_assessment = "Moderate statistical power"
    else:
        power_assessment = "Limited statistical power"
    
    print(f"     Statistical Power: {power_assessment}")
    
    # Data collection efficiency
    print(f"\n   ⚡ DATA COLLECTION EFFICIENCY:")
    print(f"     Time Per Tester: ~36 minutes (3 min/question)")
    print(f"     Completion Rate: Expected higher due to reduced fatigue")
    print(f"     Data Quality: Expected better due to maintained focus")
    print(f"     Recruitment: Easier due to shorter time commitment")

def analyze_question_diversity_impact():
    """Analyze impact on question diversity and coverage"""
    
    print(f"\n🎯 QUESTION DIVERSITY IMPACT:")
    print("=" * 40)
    
    # Load questions
    with open('data/eval_questions.json', 'r') as f:
        questions = json.load(f)
    
    retail_questions = questions['retail']
    finance_questions = questions['finance']
    
    # Analyze question types
    retail_types = []
    for q in retail_questions:
        if "revenue" in q.lower():
            retail_types.append("Revenue")
        elif "transaction" in q.lower():
            retail_types.append("Transaction")
        elif "sales" in q.lower():
            retail_types.append("Sales")
        elif "product" in q.lower():
            retail_types.append("Product")
        elif "region" in q.lower():
            retail_types.append("Regional")
        else:
            retail_types.append("Other")
    
    finance_types = []
    for q in finance_questions:
        if "price" in q.lower():
            finance_types.append("Price")
        elif "volume" in q.lower():
            finance_types.append("Volume")
        elif "trend" in q.lower():
            finance_types.append("Trend")
        elif "volatility" in q.lower():
            finance_types.append("Volatility")
        elif "correlation" in q.lower():
            finance_types.append("Correlation")
        else:
            finance_types.append("Other")
    
    print(f"   Question Type Distribution:")
    
    retail_type_counts = Counter(retail_types)
    print(f"\n   Retail Types:")
    for qtype, count in retail_type_counts.items():
        print(f"     {qtype}: {count} questions")
    
    finance_type_counts = Counter(finance_types)
    print(f"\n   Finance Types:")
    for qtype, count in finance_type_counts.items():
        print(f"     {qtype}: {count} questions")
    
    # Analyze random selection impact on diversity
    print(f"\n   🎲 RANDOM SELECTION DIVERSITY:")
    print(f"     With 6 random questions per industry:")
    print(f"     - Expected to cover most question types")
    print(f"     - Some types may be underrepresented")
    print(f"     - Provides good balance of diversity")
    print(f"     - Reduces bias toward specific question types")

def analyze_implementation_benefits():
    """Analyze benefits of the current random selection approach"""
    
    print(f"\n✅ IMPLEMENTATION BENEFITS:")
    print("=" * 40)
    
    print(f"   🎯 ADVANTAGES:")
    print(f"     ✅ Reduces tester fatigue (12 vs 20 questions)")
    print(f"     ✅ Maintains question diversity through randomization")
    print(f"     ✅ Prevents bias toward specific question types")
    print(f"     ✅ Ensures balanced industry representation")
    print(f"     ✅ Improves completion rates")
    print(f"     ✅ Faster data collection")
    print(f"     ✅ Better data quality due to maintained focus")
    
    print(f"\n   📊 STATISTICAL BENEFITS:")
    print(f"     ✅ Good statistical power (48 evaluations per tester)")
    print(f"     ✅ Random sampling reduces selection bias")
    print(f"     ✅ Representative coverage of question space")
    print(f"     ✅ Adequate sample size for meaningful analysis")
    
    print(f"\n   🔄 OPERATIONAL BENEFITS:")
    print(f"     ✅ Easier tester recruitment")
    print(f"     ✅ Consistent evaluation experience")
    print(f"     ✅ Scalable to larger sample sizes")
    print(f"     ✅ Maintains evaluation rigor")

def analyze_potential_concerns():
    """Analyze potential concerns with random selection"""
    
    print(f"\n⚠️ POTENTIAL CONCERNS:")
    print("=" * 40)
    
    print(f"   📉 COVERAGE CONCERNS:")
    print(f"     ⚠️  Some questions may be rarely selected")
    print(f"     ⚠️  Question type balance may vary between testers")
    print(f"     ⚠️  Less comprehensive coverage of all scenarios")
    print(f"     ⚠️  May miss edge cases or specific question types")
    
    print(f"\n   📊 ANALYSIS CONCERNS:")
    print(f"     ⚠️  Question-specific analysis limited")
    print(f"     ⚠️  Harder to compare specific questions across testers")
    print(f"     ⚠️  May need larger sample sizes for question-specific insights")
    print(f"     ⚠️  Statistical power varies by question frequency")
    
    print(f"\n   🔄 MITIGATION STRATEGIES:")
    print(f"     ✅ Monitor question selection frequency")
    print(f"     ✅ Ensure adequate sample size")
    print(f"     ✅ Focus on LLM comparison rather than question-specific analysis")
    print(f"     ✅ Use aggregated metrics for overall assessment")

def provide_recommendations():
    """Provide recommendations for the current approach"""
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("=" * 40)
    
    print(f"   🎯 OPTIMAL APPROACH:")
    print(f"     Current implementation is well-designed!")
    print(f"     Rationale:")
    print(f"       • Balances comprehensiveness with efficiency")
    print(f"       • Maintains statistical rigor")
    print(f"       • Reduces tester fatigue")
    print(f"       • Ensures question diversity")
    
    print(f"\n   📋 MONITORING SUGGESTIONS:")
    print(f"     1. Track question selection frequency")
    print(f"     2. Monitor completion rates")
    print(f"     3. Ensure balanced industry representation")
    print(f"     4. Validate statistical power")
    print(f"     5. Compare results across different question sets")
    
    print(f"\n   🔄 FUTURE CONSIDERATIONS:")
    print(f"     • Consider stratified sampling for better balance")
    print(f"     • Monitor for question selection bias")
    print(f"     • Adjust sample size based on results")
    print(f"     • Consider adaptive question selection")

def main():
    """Main analysis function"""
    
    # Run all analyses
    questions, evaluations = analyze_current_random_selection()
    retail_counts, finance_counts = simulate_random_selection_impact()
    analyze_data_collection_impact()
    analyze_question_diversity_impact()
    analyze_implementation_benefits()
    analyze_potential_concerns()
    provide_recommendations()
    
    print(f"\n" + "=" * 60)
    print("✅ Random Selection Analysis Complete!")

if __name__ == "__main__":
    main() 