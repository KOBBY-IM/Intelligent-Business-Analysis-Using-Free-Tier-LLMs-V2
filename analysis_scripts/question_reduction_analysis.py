#!/usr/bin/env python3
"""
Analysis of the impact of reducing blind evaluation questions
"""

import json
import pandas as pd
from typing import List, Dict, Tuple
import numpy as np

def analyze_current_question_set():
    """Analyze the current question set and evaluation data"""
    
    print("🔍 BLIND EVALUATION QUESTION REDUCTION ANALYSIS")
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
    
    print(f"\n📊 CURRENT QUESTION SET ANALYSIS:")
    
    # Count questions by industry
    retail_questions = len(questions['retail'])
    finance_questions = len(questions['finance'])
    total_questions = retail_questions + finance_questions
    
    print(f"   Total Questions: {total_questions}")
    print(f"   Retail Questions: {retail_questions}")
    print(f"   Finance Questions: {finance_questions}")
    print(f"   Questions per Industry: {total_questions/2}")
    
    # Analyze evaluation data
    print(f"\n📈 CURRENT EVALUATION DATA:")
    print(f"   Total Evaluations: {len(evaluations)}")
    
    if evaluations:
        unique_testers = len(set(eval['tester_email'] for eval in evaluations))
        print(f"   Unique Testers: {unique_testers}")
        
        # Count questions evaluated
        evaluated_questions = set()
        for eval in evaluations:
            if 'current_question' in eval:
                evaluated_questions.add(eval['current_question'])
        
        print(f"   Questions Evaluated: {len(evaluated_questions)}")
        print(f"   Questions Not Yet Evaluated: {total_questions - len(evaluated_questions)}")
    
    return questions, evaluations, total_questions

def analyze_question_reduction_scenarios():
    """Analyze different question reduction scenarios"""
    
    print(f"\n🎯 QUESTION REDUCTION SCENARIOS:")
    print("=" * 40)
    
    scenarios = [
        {"name": "Conservative (80%)", "reduction": 0.2, "questions": 16},
        {"name": "Moderate (60%)", "reduction": 0.4, "questions": 12},
        {"name": "Aggressive (40%)", "reduction": 0.6, "questions": 8},
        {"name": "Minimal (20%)", "reduction": 0.8, "questions": 4}
    ]
    
    for scenario in scenarios:
        print(f"\n   {scenario['name']}:")
        print(f"     Questions per Industry: {scenario['questions']//2}")
        print(f"     Total Questions: {scenario['questions']}")
        print(f"     Reduction: {scenario['reduction']*100:.0f}%")
        
        # Calculate evaluation time impact
        avg_time_per_question = 3  # minutes
        total_time = scenario['questions'] * avg_time_per_question
        print(f"     Estimated Time: {total_time} minutes per tester")

def analyze_statistical_impact():
    """Analyze statistical impact of question reduction"""
    
    print(f"\n📊 STATISTICAL IMPACT ANALYSIS:")
    print("=" * 40)
    
    # Current setup: 20 questions, 4 LLMs = 80 evaluations per tester
    current_evaluations_per_tester = 20 * 4
    
    scenarios = [
        {"questions": 16, "name": "16 Questions"},
        {"questions": 12, "name": "12 Questions"},
        {"questions": 8, "name": "8 Questions"},
        {"questions": 4, "name": "4 Questions"}
    ]
    
    print(f"   Current: {current_evaluations_per_tester} evaluations per tester")
    
    for scenario in scenarios:
        evaluations_per_tester = scenario['questions'] * 4
        reduction = (current_evaluations_per_tester - evaluations_per_tester) / current_evaluations_per_tester
        
        print(f"\n   {scenario['name']}:")
        print(f"     Evaluations per Tester: {evaluations_per_tester}")
        print(f"     Reduction: {reduction*100:.0f}%")
        
        # Statistical power analysis
        if evaluations_per_tester >= 30:
            power_assessment = "Good statistical power"
        elif evaluations_per_tester >= 20:
            power_assessment = "Moderate statistical power"
        elif evaluations_per_tester >= 10:
            power_assessment = "Limited statistical power"
        else:
            power_assessment = "Insufficient for reliable analysis"
        
        print(f"     Statistical Power: {power_assessment}")

def analyze_data_consistency_impact():
    """Analyze impact on data consistency and reliability"""
    
    print(f"\n🔍 DATA CONSISTENCY IMPACT:")
    print("=" * 40)
    
    # Current data analysis
    current_questions = 20
    current_llms = 4
    current_total_evaluations = current_questions * current_llms
    
    print(f"   Current Setup:")
    print(f"     Total Evaluations: {current_total_evaluations}")
    print(f"     Evaluations per LLM: {current_questions}")
    print(f"     Coverage: Complete (all questions for all LLMs)")
    
    scenarios = [
        {"questions": 16, "name": "16 Questions"},
        {"questions": 12, "name": "12 Questions"},
        {"questions": 8, "name": "8 Questions"},
        {"questions": 4, "name": "4 Questions"}
    ]
    
    for scenario in scenarios:
        total_evaluations = scenario['questions'] * current_llms
        coverage_percentage = (scenario['questions'] / current_questions) * 100
        
        print(f"\n   {scenario['name']}:")
        print(f"     Total Evaluations: {total_evaluations}")
        print(f"     Evaluations per LLM: {scenario['questions']}")
        print(f"     Question Coverage: {coverage_percentage:.0f}%")
        
        # Reliability assessment
        if coverage_percentage >= 80:
            reliability = "High - Good coverage maintained"
        elif coverage_percentage >= 60:
            reliability = "Moderate - Adequate coverage"
        elif coverage_percentage >= 40:
            reliability = "Limited - Reduced coverage"
        else:
            reliability = "Low - Minimal coverage"
        
        print(f"     Reliability: {reliability}")

def analyze_implementation_impact():
    """Analyze implementation and operational impact"""
    
    print(f"\n⚙️ IMPLEMENTATION IMPACT:")
    print("=" * 40)
    
    print(f"   Data Collection Impact:")
    print(f"     ✅ Existing data remains valid")
    print(f"     ✅ No data loss from current evaluations")
    print(f"     ⚠️  Future evaluations will have fewer questions")
    print(f"     ⚠️  Need to update question selection logic")
    
    print(f"\n   Analysis Impact:")
    print(f"     ✅ Statistical analysis methods remain the same")
    print(f"     ✅ Comparison metrics still valid")
    print(f"     ⚠️  Reduced sample size for each LLM")
    print(f"     ⚠️  May need to adjust confidence intervals")
    
    print(f"\n   User Experience Impact:")
    print(f"     ✅ Faster evaluation completion")
    print(f"     ✅ Reduced tester fatigue")
    print(f"     ✅ Higher completion rates expected")
    print(f"     ⚠️  Less comprehensive evaluation")

def provide_recommendations():
    """Provide recommendations for question reduction"""
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("=" * 40)
    
    print(f"   🎯 OPTIMAL REDUCTION SCENARIO:")
    print(f"     Recommended: 12-16 questions (60-80% of current)")
    print(f"     Rationale:")
    print(f"       • Maintains good statistical power")
    print(f"       • Preserves question diversity")
    print(f"       • Reduces tester fatigue")
    print(f"       • Balances comprehensiveness with efficiency")
    
    print(f"\n   📋 IMPLEMENTATION STEPS:")
    print(f"     1. Select most representative questions from each industry")
    print(f"     2. Ensure balanced coverage of question types")
    print(f"     3. Update eval_questions.json with reduced set")
    print(f"     4. Regenerate pregenerated responses for new set")
    print(f"     5. Update analysis scripts if needed")
    
    print(f"\n   ⚠️  CONSIDERATIONS:")
    print(f"     • Existing data remains valuable for baseline comparison")
    print(f"     • Consider A/B testing with different question sets")
    print(f"     • Monitor completion rates and data quality")
    print(f"     • May need to adjust sample size requirements")

def analyze_question_selection_strategy():
    """Analyze strategies for selecting which questions to keep"""
    
    print(f"\n🎯 QUESTION SELECTION STRATEGIES:")
    print("=" * 40)
    
    # Load current questions
    with open('data/eval_questions.json', 'r') as f:
        questions = json.load(f)
    
    print(f"   Current Question Types:")
    
    # Analyze retail questions
    retail_questions = questions['retail']
    print(f"\n   Retail Questions ({len(retail_questions)}):")
    for i, q in enumerate(retail_questions, 1):
        question_type = "Revenue" if "revenue" in q.lower() else "Transaction" if "transaction" in q.lower() else "Sales" if "sales" in q.lower() else "Product" if "product" in q.lower() else "Regional" if "region" in q.lower() else "Other"
        print(f"     {i}. {question_type}: {q[:50]}...")
    
    # Analyze finance questions
    finance_questions = questions['finance']
    print(f"\n   Finance Questions ({len(finance_questions)}):")
    for i, q in enumerate(finance_questions, 1):
        question_type = "Price" if "price" in q.lower() else "Volume" if "volume" in q.lower() else "Trend" if "trend" in q.lower() else "Volatility" if "volatility" in q.lower() else "Correlation" if "correlation" in q.lower() else "Other"
        print(f"     {i}. {question_type}: {q[:50]}...")
    
    print(f"\n   Selection Criteria:")
    print(f"     • Question diversity (different types)")
    print(f"     • Complexity variation (simple to complex)")
    print(f"     • Industry representation")
    print(f"     • Analytical depth required")

def main():
    """Main analysis function"""
    
    # Run all analyses
    questions, evaluations, total_questions = analyze_current_question_set()
    analyze_question_reduction_scenarios()
    analyze_statistical_impact()
    analyze_data_consistency_impact()
    analyze_implementation_impact()
    analyze_question_selection_strategy()
    provide_recommendations()
    
    print(f"\n" + "=" * 60)
    print("✅ Question Reduction Analysis Complete!")

if __name__ == "__main__":
    main() 