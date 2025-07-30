#!/usr/bin/env python3
"""
Analysis of reducing questions from 6 to 4 per industry on existing data
"""

import json
import pandas as pd
from typing import List, Dict, Tuple
from collections import Counter

def analyze_existing_data_impact():
    """Analyze impact on existing evaluation data"""
    
    print("📊 EXISTING DATA IMPACT ANALYSIS")
    print("=" * 60)
    
    # Load existing evaluation data
    try:
        with open('data/evaluations.json', 'r') as f:
            evaluations = json.load(f)
    except:
        evaluations = []
    
    print(f"\n📈 CURRENT DATA STATUS:")
    print(f"   Total Evaluations: {len(evaluations)}")
    
    if evaluations:
        unique_testers = len(set(eval['tester_email'] for eval in evaluations))
        print(f"   Unique Testers: {unique_testers}")
        
        # Analyze questions evaluated
        evaluated_questions = set()
        for eval in evaluations:
            if 'current_question' in eval:
                evaluated_questions.add(eval['current_question'])
        
        print(f"   Questions Evaluated: {len(evaluated_questions)}")
        print(f"   Questions Not Yet Evaluated: {20 - len(evaluated_questions)}")
        
        # Analyze industry coverage
        retail_questions = [q for q in evaluated_questions if any(retail_term in q.lower() for retail_term in ['product', 'category', 'revenue', 'sales', 'region'])]
        finance_questions = [q for q in evaluated_questions if any(finance_term in q.lower() for finance_term in ['price', 'stock', 'volume', 'trend', 'volatility'])]
        
        print(f"   Retail Questions Evaluated: {len(retail_questions)}")
        print(f"   Finance Questions Evaluated: {len(finance_questions)}")
    
    return evaluations

def analyze_reduction_scenarios():
    """Analyze different reduction scenarios"""
    
    print(f"\n🎯 REDUCTION SCENARIOS ANALYSIS:")
    print("=" * 40)
    
    scenarios = [
        {"current": 6, "proposed": 4, "name": "6 → 4 Questions"},
        {"current": 6, "proposed": 3, "name": "6 → 3 Questions"},
        {"current": 6, "proposed": 2, "name": "6 → 2 Questions"}
    ]
    
    for scenario in scenarios:
        current = scenario["current"]
        proposed = scenario["proposed"]
        reduction = ((current - proposed) / current) * 100
        
        print(f"\n   {scenario['name']}:")
        print(f"     Current: {current} questions per industry")
        print(f"     Proposed: {proposed} questions per industry")
        print(f"     Reduction: {reduction:.0f}%")
        print(f"     Total Questions: {proposed * 2} (vs current {current * 2})")
        print(f"     Evaluations per Tester: {proposed * 2 * 4} (vs current {current * 2 * 4})")
        print(f"     Time per Tester: ~{proposed * 2 * 3} minutes (vs current {current * 2 * 3})")

def analyze_statistical_impact():
    """Analyze statistical impact of reduction"""
    
    print(f"\n📊 STATISTICAL IMPACT ANALYSIS:")
    print("=" * 40)
    
    # Current vs proposed scenarios
    scenarios = [
        {"questions": 6, "name": "Current (6 per industry)"},
        {"questions": 4, "name": "Proposed (4 per industry)"},
        {"questions": 3, "name": "Alternative (3 per industry)"},
        {"questions": 2, "name": "Minimal (2 per industry)"}
    ]
    
    for scenario in scenarios:
        questions_per_industry = scenario["questions"]
        total_questions = questions_per_industry * 2
        evaluations_per_tester = total_questions * 4
        evaluations_per_llm = total_questions
        
        print(f"\n   {scenario['name']}:")
        print(f"     Total Questions: {total_questions}")
        print(f"     Evaluations per Tester: {evaluations_per_tester}")
        print(f"     Evaluations per LLM: {evaluations_per_llm}")
        
        # Statistical power assessment
        if evaluations_per_llm >= 10:
            power_assessment = "Good statistical power"
        elif evaluations_per_llm >= 6:
            power_assessment = "Moderate statistical power"
        elif evaluations_per_llm >= 4:
            power_assessment = "Limited statistical power"
        else:
            power_assessment = "Insufficient for reliable analysis"
        
        print(f"     Statistical Power: {power_assessment}")
        
        # Coverage assessment
        coverage_percentage = (total_questions / 20) * 100
        if coverage_percentage >= 60:
            coverage_assessment = "Good coverage"
        elif coverage_percentage >= 40:
            coverage_assessment = "Moderate coverage"
        else:
            coverage_assessment = "Limited coverage"
        
        print(f"     Question Coverage: {coverage_percentage:.0f}% ({coverage_assessment})")

def analyze_data_compatibility():
    """Analyze compatibility with existing data"""
    
    print(f"\n🔄 DATA COMPATIBILITY ANALYSIS:")
    print("=" * 40)
    
    print(f"   ✅ EXISTING DATA PRESERVATION:")
    print(f"     • All current evaluations remain valid")
    print(f"     • No data loss from existing testers")
    print(f"     • Baseline comparison data preserved")
    print(f"     • Statistical methods remain unchanged")
    
    print(f"\n   ⚠️  COMPATIBILITY CONSIDERATIONS:")
    print(f"     • Future evaluations will have fewer questions")
    print(f"     • Question selection logic needs updating")
    print(f"     • Analysis scripts may need adjustment")
    print(f"     • Sample size requirements may change")
    
    print(f"\n   📊 COMPARISON POSSIBILITIES:")
    print(f"     • Compare old (6 questions) vs new (4 questions) data")
    print(f"     • Validate consistency between question sets")
    print(f"     • Assess impact of question reduction on results")
    print(f"     • Use existing data as baseline for new approach")

def analyze_question_selection_impact():
    """Analyze impact on question selection and diversity"""
    
    print(f"\n🎯 QUESTION SELECTION IMPACT:")
    print("=" * 40)
    
    # Load current questions
    with open('data/eval_questions.json', 'r') as f:
        questions = json.load(f)
    
    retail_questions = questions['retail']
    finance_questions = questions['finance']
    
    print(f"   Current Question Distribution:")
    print(f"     Retail: {len(retail_questions)} questions")
    print(f"     Finance: {len(finance_questions)} questions")
    
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
    
    retail_type_counts = Counter(retail_types)
    finance_type_counts = Counter(finance_types)
    
    print(f"\n   Question Type Distribution:")
    print(f"     Retail Types: {dict(retail_type_counts)}")
    print(f"     Finance Types: {dict(finance_type_counts)}")
    
    print(f"\n   Impact of 4 Questions per Industry:")
    print(f"     • Retail: 4/10 questions (40% coverage)")
    print(f"     • Finance: 4/10 questions (40% coverage)")
    print(f"     • Expected to cover 2-3 question types per industry")
    print(f"     • Some question types may be underrepresented")

def analyze_user_experience_impact():
    """Analyze impact on user experience"""
    
    print(f"\n👥 USER EXPERIENCE IMPACT:")
    print("=" * 40)
    
    scenarios = [
        {"questions": 6, "name": "Current (6 per industry)"},
        {"questions": 4, "name": "Proposed (4 per industry)"},
        {"questions": 3, "name": "Alternative (3 per industry)"},
        {"questions": 2, "name": "Minimal (2 per industry)"}
    ]
    
    for scenario in scenarios:
        questions_per_industry = scenario["questions"]
        total_questions = questions_per_industry * 2
        estimated_time = total_questions * 3  # 3 minutes per question
        
        print(f"\n   {scenario['name']}:")
        print(f"     Total Questions: {total_questions}")
        print(f"     Estimated Time: {estimated_time} minutes")
        print(f"     Evaluations: {total_questions * 4}")
        
        # User experience assessment
        if estimated_time <= 20:
            experience = "Excellent - Very manageable"
        elif estimated_time <= 30:
            experience = "Good - Reasonable commitment"
        elif estimated_time <= 40:
            experience = "Moderate - Some fatigue possible"
        else:
            experience = "Challenging - High fatigue risk"
        
        print(f"     User Experience: {experience}")

def analyze_research_implications():
    """Analyze implications for research validity"""
    
    print(f"\n🔬 RESEARCH IMPLICATIONS:")
    print("=" * 40)
    
    print(f"   📊 VALIDITY CONSIDERATIONS:")
    print(f"     • Statistical Power: 8 evaluations per LLM (4 questions)")
    print(f"     • Question Coverage: 40% of available questions")
    print(f"     • Industry Representation: Balanced (4 each)")
    print(f"     • Sample Size Requirements: May need more testers")
    
    print(f"\n   ✅ POSITIVE IMPACTS:")
    print(f"     • Higher completion rates expected")
    print(f"     • Better data quality due to reduced fatigue")
    print(f"     • Easier recruitment of testers")
    print(f"     • Faster data collection")
    
    print(f"\n   ⚠️  POTENTIAL RISKS:")
    print(f"     • Limited question diversity")
    print(f"     • Reduced statistical power")
    print(f"     • May miss important question types")
    print(f"     • Harder to generalize results")
    
    print(f"\n   🎯 MITIGATION STRATEGIES:")
    print(f"     • Increase sample size to compensate")
    print(f"     • Use stratified sampling for question types")
    print(f"     • Focus on LLM comparison rather than question-specific analysis")
    print(f"     • Validate results with existing 6-question data")

def provide_recommendations():
    """Provide recommendations for the reduction"""
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("=" * 40)
    
    print(f"   🎯 OPTIMAL APPROACH:")
    print(f"     Consider 4 questions per industry with conditions:")
    print(f"     Rationale:")
    print(f"       • Maintains adequate statistical power")
    print(f"       • Significantly improves user experience")
    print(f"       • Preserves research validity")
    print(f"       • Balances efficiency with rigor")
    
    print(f"\n   📋 IMPLEMENTATION STRATEGY:")
    print(f"     1. Use existing 6-question data as baseline")
    print(f"     2. Implement 4-question approach for new testers")
    print(f"     3. Compare results between approaches")
    print(f"     4. Increase sample size to compensate for reduced questions")
    print(f"     5. Use stratified sampling to ensure question type diversity")
    
    print(f"\n   ⚠️  CRITICAL CONSIDERATIONS:")
    print(f"     • Minimum 8 evaluations per LLM (moderate power)")
    print(f"     • Need larger sample size for statistical significance")
    print(f"     • Question selection must ensure type diversity")
    print(f"     • Monitor for bias in question selection")
    
    print(f"\n   🔄 ALTERNATIVE APPROACHES:")
    print(f"     • Hybrid: 4 questions for initial screening, 6 for detailed analysis")
    print(f"     • Adaptive: Adjust based on completion rates and data quality")
    print(f"     • Stratified: Ensure each question type is represented")
    print(f"     • Phased: Start with 4, increase to 6 if needed")

def main():
    """Main analysis function"""
    
    # Run all analyses
    evaluations = analyze_existing_data_impact()
    analyze_reduction_scenarios()
    analyze_statistical_impact()
    analyze_data_compatibility()
    analyze_question_selection_impact()
    analyze_user_experience_impact()
    analyze_research_implications()
    provide_recommendations()
    
    print(f"\n" + "=" * 60)
    print("✅ Question Reduction Impact Analysis Complete!")

if __name__ == "__main__":
    main() 