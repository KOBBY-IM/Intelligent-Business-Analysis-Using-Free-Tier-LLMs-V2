"""
Blind Evaluation Page

This page presents pregenerated LLM responses to external testers in a blind fashion,
collecting structured feedback on quality, relevance, accuracy, and uniformity.
"""

import streamlit as st
import json
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Blind Evaluation - LLM Comparison",
    page_icon="🔍",
    layout="wide"
)

def load_evaluation_data() -> Tuple[Dict, List[Dict]]:
    """
    Load evaluation questions and pregenerated responses.
    
    Returns:
        Tuple of (questions_dict, responses_list)
    """
    try:
        # Load questions
        questions_path = os.path.join('data', 'eval_questions.json')
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        # Load pregenerated responses
        responses_path = os.path.join('data', 'pregenerated_responses.json')
        if os.path.exists(responses_path):
            with open(responses_path, 'r', encoding='utf-8') as f:
                responses = json.load(f)
                # If responses is empty or not a list, create sample responses
                if not responses or not isinstance(responses, list):
                    responses = create_sample_responses(questions)
        else:
            # Create sample responses for testing
            responses = create_sample_responses(questions)
        
        return questions, responses
    except Exception as e:
        st.error(f"Error loading evaluation data: {str(e)}")
        st.error(f"Debug: questions_path = {os.path.join('data', 'eval_questions.json')}")
        st.error(f"Debug: responses_path = {os.path.join('data', 'pregenerated_responses.json')}")
        return {}, []

def create_sample_responses(questions: Dict) -> List[Dict]:
    """
    Create sample responses for testing when no pregenerated responses exist.
    
    Args:
        questions: Dictionary of questions by industry
    
    Returns:
        List of sample response dictionaries
    """
    sample_responses = []
    llm_models = ["Model A", "Model B", "Model C", "Model D"]
    
    for industry, question_list in questions.items():
        for question in question_list:
            for i, model in enumerate(llm_models):
                # Create more varied and realistic sample responses
                if industry == "retail":
                    response_templates = [
                        f"Based on our retail analysis, {model} suggests that the key factors affecting this metric include customer behavior patterns, seasonal trends, and market competition. The data indicates a need for strategic adjustments in pricing and inventory management.",
                        f"{model} analysis shows that this retail question requires examining multiple data points including sales velocity, customer demographics, and regional performance variations. The insights suggest focusing on high-performing segments.",
                        f"From a retail perspective, {model} identifies that this business challenge involves understanding customer preferences, market positioning, and operational efficiency. The recommended approach includes data-driven decision making."
                    ]
                else:  # finance
                    response_templates = [
                        f"Financial analysis by {model} indicates that this metric is influenced by market volatility, regulatory changes, and economic indicators. The model suggests monitoring key risk factors and adjusting portfolio strategies accordingly.",
                        f"{model} financial assessment reveals that this question requires analyzing market trends, risk exposure, and performance benchmarks. The findings suggest implementing robust risk management protocols.",
                        f"From a finance standpoint, {model} determines that this analysis involves examining market correlations, volatility patterns, and regulatory impacts. The recommendations focus on strategic positioning and risk mitigation."
                    ]
                
                # Select a random template and customize it
                import random
                template = random.choice(response_templates)
                response = template.replace("{model}", model)
                
                sample_responses.append({
                    "industry": industry,
                    "question": question,
                    "llm_provider": f"provider_{i+1}",
                    "llm_model": model,
                    "response": response,
                    "context": [f"Sample {industry} context 1", f"Sample {industry} context 2"],
                    "prompt": f"Sample prompt for {question}",
                    "error": None,
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    return sample_responses

def get_responses_for_question(question: str, industry: str, responses: List[Dict]) -> List[Dict]:
    """
    Get all responses for a specific question and industry.
    
    Args:
        question: The question text
        industry: The industry (retail/finance)
        responses: List of all responses
    
    Returns:
        List of responses for the specific question
    """
    matching_responses = []
    for response in responses:
        if (response.get("question") == question and 
            response.get("industry") == industry and 
            response.get("error") is None):
            matching_responses.append(response)
    return matching_responses

def shuffle_responses(responses: List[Dict]) -> List[Dict]:
    """
    Shuffle responses to ensure anonymity.
    
    Args:
        responses: List of response dictionaries
    
    Returns:
        Shuffled list of responses with anonymous IDs
    """
    # Create a copy to avoid modifying the original
    shuffled = responses.copy()
    random.shuffle(shuffled)
    
    # Add anonymous IDs (A, B, C, D)
    for i, response in enumerate(shuffled):
        response["anonymous_id"] = chr(65 + i)  # A, B, C, D
    
    return shuffled

def display_evaluation_instructions():
    """Display clear instructions for testers."""
    st.markdown("""
    ## 📋 Evaluation Instructions
    
    You will be presented with business analysis questions and responses from different AI models. 
    **You will not know which model generated each response** - they are labeled as Response A, B, C, and D.
    
    ### 🎯 Ground Truth Answer & Context
    Before evaluating each response, you will see a **"Ground Truth Answer & Context"** section that provides:
    - **🎯 The correct answer** to the question based on actual dataset analysis
    - **📊 Key statistics and metrics** from the real data
    - **📈 Important insights** that should be mentioned in good responses
    - **🔍 Factual background** to help you assess response accuracy
    
    **Use this ground truth information as your primary reference** when evaluating the AI responses. Compare each response against these facts to assess accuracy and completeness.
    
    ### How to Evaluate Each Response:
    
    **Quality (1-5 scale):**
    - 1 = Poor: Unclear, confusing, or unhelpful
    - 2 = Below Average: Some useful information but major issues
    - 3 = Average: Adequate but not exceptional
    - 4 = Good: Clear, helpful, and well-structured
    - 5 = Excellent: Outstanding clarity, insight, and usefulness
    
    **Relevance (1-5 scale):**
    - 1 = Not Relevant: Doesn't address the question
    - 2 = Slightly Relevant: Tangentially related
    - 3 = Somewhat Relevant: Partially addresses the question
    - 4 = Relevant: Directly addresses the question
    - 5 = Highly Relevant: Perfectly addresses the question with precision
    
    **Accuracy (1-5 scale):**
    - 1 = Inaccurate: Contains errors or contradicts ground truth data
    - 2 = Mostly Inaccurate: Several errors when compared to ground truth
    - 3 = Somewhat Accurate: Mix of correct and incorrect information vs ground truth
    - 4 = Accurate: Generally aligns with ground truth with minor issues
    - 5 = Highly Accurate: Factually correct and matches ground truth data
    
    **Uniformity (1-5 scale):**
    - 1 = Inconsistent: Contradictory or poorly organized
    - 2 = Somewhat Inconsistent: Some organization issues
    - 3 = Moderately Consistent: Generally well-organized
    - 4 = Consistent: Well-structured and organized
    - 5 = Highly Consistent: Excellent structure and flow
    
    ### 📝 Evaluation Process:
    
    1. **Rate Each Response**: Provide ratings for Quality, Relevance, Accuracy, and Uniformity for each response
    2. **Submit & Continue**: Click "Submit & Continue" to save ratings and move to the next question
    3. **Complete All Questions**: Continue through all questions for both industries
    4. **Provide Final Written Feedback**: At the end, provide comprehensive written feedback on overall impressions
    
    ### 📊 Final Assessment:
    
    After completing all questions, you will provide:
    - **Overall ratings** for quality, relevance, accuracy, and usefulness
    - **Detailed written feedback** on strengths and weaknesses
    - **Suggestions** for improving AI business analysis
    - **General observations** about the evaluation experience
    
    **Note**: Individual ratings are collected for each response, but detailed written feedback is provided only at the end!
    """)

def display_dataset_overview():
    """Display comprehensive overview of the datasets used in evaluation."""
    st.markdown("""
    ## 📊 Dataset Overview
    
    This evaluation uses two comprehensive business datasets that serve as the knowledge base for AI model responses. Understanding these datasets will help you better assess the accuracy and relevance of the AI responses.
    
    ### 🛍️ Retail Dataset: E-commerce Shopping Trends
    **File:** `shopping_trends_with_rag.csv`
    
    **📈 Scale & Scope:**
    - **3,900 purchase records** across 20 data fields
    - **$233,081 total revenue** with $59.76 average purchase
    - Customer IDs ranging from 1 to 3,900
    
    **🛍️ Product Categories (Revenue Distribution):**
    - **Clothing**: $104,264 (44.7%) - 1,737 purchases
    - **Accessories**: $74,200 (31.8%) - 1,240 purchases  
    - **Footwear**: $36,093 (15.5%) - 599 purchases
    - **Outerwear**: $18,524 (7.9%) - 324 purchases
    
    **👥 Customer Demographics:**
    - **Age Range**: 18-70 years
    - **Gender Split**: 68% Male, 32% Female
    - **Geographic Coverage**: All 50 US states
    - **Top Revenue States**: Montana, Illinois, California, Idaho, Nevada
    
    **💳 Business Operations:**
    - **Payment Methods**: Credit Card, Venmo, Cash, PayPal, Debit Card, Bank Transfer (evenly distributed ~16-18% each)
    - **Seasonal Distribution**: Spring (25.6%), Fall (25.0%), Winter (24.9%), Summer (24.5%)
    - **Customer Satisfaction**: Average rating 3.75/5.0 (range: 2.5-5.0)
    
    ### 📈 Finance Dataset: Tesla Stock Analysis
    **File:** `Tesla_stock_data_with_rag.csv`
    
    **📊 Market Data:**
    - **3,782 trading days** from June 29, 2010 to July 11, 2025
    - **Complete OHLCV data**: Open, High, Low, Close, Volume
    - **Price Range**: $1.00 (lowest) to $488.54 (highest)
    - **Current Price**: $313.51
    
    **📈 Performance Metrics:**
    - **Total Return**: +19,584.59% (from $1.59 to $313.51)
    - **Average Close**: $89.59
    - **Volatility**: 3.66% daily, 58.13% annualized
    - **Total Volume**: 367 billion shares traded
    
    **📅 Historical Trends:**
    - **2010-2019**: Early growth phase ($1.56-$20.95 average)
    - **2020**: Breakout year ($96.67 average, 57B volume)
    - **2021-2022**: Peak performance ($260-$263 average)
    - **2023-2025**: Stabilization ($217-$316 average)
    
    ### 🎯 Purpose in LLM Evaluation
    
    These datasets serve as the **knowledge base for the RAG (Retrieval-Augmented Generation) system** that:
    
    1. **Grounds LLM Responses**: Provides factual business data for AI models to reference
    2. **Enables Business Analysis**: Covers key business domains (retail e-commerce and financial markets)
    3. **Supports Evaluation Questions**: Contains the data needed to answer the evaluation questions
    4. **Ensures Accuracy**: Allows comparison between AI responses and actual dataset statistics
    
    ### 🔧 How They're Used
    
    - **RAG Pipeline**: Documents are chunked, embedded, and stored for retrieval
    - **Evaluation Questions**: Questions reference specific aspects of these datasets
    - **Ground Truth**: Actual statistics from these datasets form the "correct" answers
    - **AI Responses**: Models generate responses based on retrieved context from these datasets
    
    The datasets provide a realistic business intelligence scenario where AI models must analyze customer behavior, sales performance, market trends, and financial metrics to provide actionable insights.
    """)

def display_question_and_responses(question: str, industry: str, responses: List[Dict], question_number: int = None):
    """
    Display a question and its shuffled responses for evaluation.
    
    Args:
        question: The question to display
        industry: The industry context
        responses: List of responses to display (should be shuffled)
        question_number: The current question number (optional)
    """
    if question_number is not None:
        st.markdown(f"### 🎯 Question {question_number} of 6 ({industry.title()} Industry)")
    else:
        st.markdown(f"### 🎯 Question ({industry.title()} Industry)")
    st.markdown(f"**{question}**")
    st.markdown("---")
    
    # Display ground truth information to aid evaluation
    st.markdown("### 🎯 Ground Truth Answer & Context")
    ground_truth = get_ground_truth_for_question(question, industry)
    st.markdown(ground_truth)
    st.markdown("---")
    
    # Display each response
    for response in responses:
        anonymous_id = response.get("anonymous_id", "Unknown")
        response_text = response.get("response", "No response available")
        
        st.markdown(f"#### Response {anonymous_id}")
        
        # Response text in an expander
        with st.expander(f"View Response {anonymous_id}", expanded=True):
            st.markdown(response_text)
        
        # Rating section (keep ratings, remove comments)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            quality_rating = st.selectbox(
                f"Quality Rating",
                options=[1, 2, 3, 4, 5],
                key=f"quality_{anonymous_id}",
                help="Rate the overall quality of this response"
            )
        
        with col2:
            relevance_rating = st.selectbox(
                f"Relevance Rating",
                options=[1, 2, 3, 4, 5],
                key=f"relevance_{anonymous_id}",
                help="Rate how relevant this response is to the question"
            )
        
        with col3:
            accuracy_rating = st.selectbox(
                f"Accuracy Rating",
                options=[1, 2, 3, 4, 5],
                key=f"accuracy_{anonymous_id}",
                help="Rate the factual accuracy of this response"
            )
        
        with col4:
            uniformity_rating = st.selectbox(
                f"Uniformity Rating",
                options=[1, 2, 3, 4, 5],
                key=f"uniformity_{anonymous_id}",
                help="Rate the consistency and organization of this response"
            )
        
        # Store ratings in session state (without comments)
        st.session_state[f"ratings_{anonymous_id}"] = {
            "quality": quality_rating,
            "relevance": relevance_rating,
            "accuracy": accuracy_rating,
            "uniformity": uniformity_rating,
            "response_id": response.get("llm_model", "unknown")
        }
        
        st.markdown("---")

def get_ground_truth_for_question(question: str, industry: str) -> str:
    """
    Get ground truth information for a specific question to aid evaluation.
    This provides actual dataset-based information to help evaluators assess response accuracy.
    
    Args:
        question: The question text
        industry: The industry (retail/finance)
    
    Returns:
        Ground truth information as markdown string
    """
    ground_truth_data = {
        "retail": {
            "Which product category generates the highest total revenue?": """
            **🎯 Ground Truth Answer: Clothing Category**
            
            **📊 Actual Dataset Statistics:**
            - **Clothing Revenue:** $104,264.00 (44.7% of total)
            - **Accessories Revenue:** $74,200.00 (31.8% of total)
            - **Footwear Revenue:** $36,093.00 (15.5% of total)
            - **Outerwear Revenue:** $18,524.00 (7.9% of total)
            - **Total Revenue:** $233,081.00
            
            **📈 Key Insights:**
            - Clothing is the dominant category by a significant margin
            - Clothing accounts for nearly half of all revenue
            - Clear hierarchy: Clothing > Accessories > Footwear > Outerwear
            - Revenue distribution shows strong category performance differences
            """,
            
            "What is the average transaction value per category?": """
            **🎯 Ground Truth Answer: Similar averages across categories**
            
            **📊 Actual Dataset Statistics:**
            - **Accessories Average:** $59.84 per transaction
            - **Clothing Average:** $60.03 per transaction
            - **Footwear Average:** $60.26 per transaction
            - **Outerwear Average:** $57.17 per transaction
            - **Overall Average:** $59.76 per transaction
            
            **📈 Key Insights:**
            - Very similar average transaction values across categories
            - Minimal variation suggests consistent pricing strategy
            - All categories perform within a narrow range
            """,
            
            "Which category has the most transactions?": """
            **🎯 Ground Truth Answer: Clothing category has the most transactions**
            
            **📊 Actual Dataset Statistics:**
            - **Clothing Transactions:** 1,737 transactions
            - **Accessories Transactions:** 1,240 transactions
            - **Footwear Transactions:** 599 transactions
            - **Outerwear Transactions:** 324 transactions
            - **Total Transactions:** 3,900 transactions
            
            **📈 Key Insights:**
            - Clothing dominates both revenue and transaction count
            - Transaction distribution mirrors revenue distribution
            - High volume drives clothing's revenue leadership
            """,
            
            "How does revenue distribution vary across product categories?": """
            **🎯 Ground Truth Answer: Highly concentrated in clothing category**
            
            **📊 Actual Dataset Statistics:**
            - **Clothing:** 44.7% of total revenue ($104,264.00)
            - **Accessories:** 31.8% of total revenue ($74,200.00)
            - **Footwear:** 15.5% of total revenue ($36,093.00)
            - **Outerwear:** 7.9% of total revenue ($18,524.00)
            
            **📈 Key Insights:**
            - Heavy concentration in clothing and accessories
            - Clear revenue hierarchy across categories
            - Significant revenue gap between top and bottom categories
            """,
            
            "Which region or location generates the highest revenue?": """
            **🎯 Ground Truth Answer: Based on actual location data**
            
            **📊 Actual Dataset Statistics:**
            - **Top Revenue Locations:** Montana ($5,784), Illinois ($5,617), California ($5,605)
            - **Geographic Distribution:** Sales across all 50 states
            
            **📈 Key Insights:**
            - Strong performance in major population centers
            - Geographic diversity in customer base
            - Regional marketing opportunities
            """,
            
            "What is the average transaction value by region?": """
            **🎯 Ground Truth Answer: Varies by region**
            
            **📊 Actual Dataset Statistics:**
            - **Top Average Locations:** Alaska ($67.60), Pennsylvania ($66.57), Arizona ($66.55)
            - **Overall Average:** $59.76 per transaction
            
            **📈 Key Insights:**
            - Regional variations in spending patterns
            - Population density affects spending
            - Market segmentation opportunities
            """,
            
            "How do sales patterns differ across different locations?": """
            **🎯 Ground Truth Answer: Significant regional variations**
            
            **📊 Actual Dataset Statistics:**
            - **Geographic Coverage:** All 50 states represented
            - **Regional Preferences:** Vary by climate and demographics
            - **Category Distribution:** Consistent across regions
            
            **📈 Key Insights:**
            - Climate affects product preferences
            - Regional culture influences buying patterns
            - Localized marketing strategies needed
            """,
            
            "Which region has the most consistent sales performance?": """
            **🎯 Ground Truth Answer: Based on transaction volume consistency**
            
            **📊 Actual Dataset Statistics:**
            - **Transaction Distribution:** Spread across all states
            - **Consistency Factors:** Population, economic factors
            - **Regional Patterns:** Vary by market size
            
            **📈 Key Insights:**
            - Larger markets provide stable revenue base
            - Predictable sales patterns aid planning
            - Portfolio diversification across regions
            """,
            
            "What are the top 5 best-selling products by revenue?": """
            **🎯 Ground Truth Answer: Based on actual product revenue data**
            
            **📊 Actual Dataset Statistics:**
            - **Top Products:** Blouse ($10,410), Shirt ($10,332), Dress ($10,320)
            - **Revenue Concentration:** Top products drive significant revenue
            
            **📈 Key Insights:**
            - Premium products drive significant revenue
            - High-value items crucial for profitability
            - Brand positioning important
            """,
            
            "Which products have the highest average transaction value?": """
            **🎯 Ground Truth Answer: Based on product category averages**
            
            **📊 Actual Dataset Statistics:**
            - **Category Averages:** Clothing ($60.03), Accessories ($59.84), Footwear ($60.26), Outerwear ($57.17)
            - **Overall Average:** $59.76 per transaction
            
            **📈 Key Insights:**
            - Premium positioning drives higher values
            - Quality perception affects pricing
            - Brand value important for margins
            """
        },
        
        "finance": {
            "What is the overall price trend over the time period?": """
            **🎯 Ground Truth Answer: Strong upward trend with massive growth**
            
            **📊 Actual Dataset Statistics:**
            - **Starting Price:** $1.59
            - **Ending Price:** $313.51
            - **Total Return:** 19,584.59%
            - **Price Range:** $1.00 to $488.54
            
            **📈 Key Insights:**
            - One of the most successful stock investments in history
            - Massive growth from startup to major company
            - Clear long-term upward trajectory
            """,
            
            "On which date did the stock reach its highest closing price?": """
            **🎯 Ground Truth Answer: 2024-12-17**
            
            **📊 Actual Dataset Statistics:**
            - **Highest Closing Price:** $479.86
            - **Date:** 2024-12-17
            - **Context:** During strong market rally and growth phase
            
            **📈 Key Insights:**
            - Peak occurred during market euphoria
            - High volatility around peak levels
            - Important resistance level for technical analysis
            """,
            
            "What is the average daily price change?": """
            **🎯 Ground Truth Answer: High volatility with significant daily swings**
            
            **📊 Actual Dataset Statistics:**
            - **Average Daily Change:** 0.21%
            - **Volatility:** 3.66%
            - **Daily Range:** 4.3%
            
            **📈 Key Insights:**
            - High daily volatility characteristic
            - Risk management crucial for investors
            - Opportunities for active trading
            """,
            
            "How many days did the stock close higher than it opened?": """
            **🎯 Ground Truth Answer: 49.6% of trading days**
            
            **📊 Actual Dataset Statistics:**
            - **Positive Close Days:** 1,877 days
            - **Negative Close Days:** 1,905 days
            - **Positive Percentage:** 49.6%
            
            **📈 Key Insights:**
            - Slight positive bias over time
            - High intraday volatility common
            - Gap trading opportunities exist
            """,
            
            "What is the correlation between opening and closing prices?": """
            **🎯 Ground Truth Answer: Strong positive correlation**
            
            **📊 Actual Dataset Statistics:**
            - **Correlation Coefficient:** 1.00
            - **Daily Range:** 4.3%
            
            **📈 Key Insights:**
            - Opening price predictive of daily direction
            - High intraday volatility despite correlation
            - Gap trading strategies possible
            """,
            
            "What is the average daily price volatility (high-low range)?": """
            **🎯 Ground Truth Answer: High daily volatility with wide ranges**
            
            **📊 Actual Dataset Statistics:**
            - **Average Daily Range:** 4.3%
            - **Volatility:** 3.66%
            
            **📈 Key Insights:**
            - High volatility characteristic of growth stock
            - Wide daily ranges provide trading opportunities
            - Risk management essential for position sizing
            """,
            
            "Which days had the largest price swings?": """
            **🎯 Ground Truth Answer: High volume days and major events**
            
            **📊 Actual Dataset Statistics:**
            - **High Volume Days:** 190 days above 241,592,475 volume
            - **Volume Threshold:** 95th percentile volume
            
            **📈 Key Insights:**
            - Volume spikes indicate major events
            - Institutional activity increases on news
            - Volume confirms price movement significance
            """,
            
            "How does the opening price trend compare to the closing price trend?": """
            **🎯 Ground Truth Answer: Both show strong upward trends**
            
            **📊 Actual Dataset Statistics:**
            - **Correlation:** 1.00
            - **Trend Alignment:** Strong correlation between open and close trends
            
            **📈 Key Insights:**
            - Both prices follow same long-term trend
            - High correlation despite daily volatility
            - Technical analysis applicable to both
            """,
            
            "What is the average daily trading volume?": """
            **🎯 Ground Truth Answer: High and variable trading volume**
            
            **📊 Actual Dataset Statistics:**
            - **Average Daily Volume:** 97,109,460 shares
            - **Volume Range:** 1,777,500 to 914,082,000 shares
            
            **📈 Key Insights:**
            - Very liquid stock with high trading activity
            - Volume spikes during major events
            - Institutional and retail participation
            """,
            
            "Are there any days with unusually high trading volume?": """
            **🎯 Ground Truth Answer: Yes, significant volume spikes on major events**
            
            **📊 Actual Dataset Statistics:**
            - **High Volume Days:** 190 days
            - **Volume Threshold:** 241,592,475 shares (95th percentile)
            
            **📈 Key Insights:**
            - Volume spikes indicate major events
            - Institutional activity increases on news
            - Retail participation spikes on volatility
            """
        }
    }
    
    # Get ground truth for the specific question
    industry_data = ground_truth_data.get(industry, {})
    ground_truth = industry_data.get(question, """
    **🎯 Ground Truth Context:**
    - **Note:** Ground truth data is being compiled for this question
    - **Evaluation Focus:** Please assess the response based on clarity, relevance, and logical reasoning
    - **Context:** Consider whether the response provides actionable business insights
    - **Data Accuracy:** Check if the response aligns with the provided dataset information
    """)
    
    return ground_truth

def collect_evaluation_data() -> Dict:
    """
    Collect all evaluation data from session state.
    
    Returns:
        Dictionary containing all evaluation data
    """
    evaluation_data = {
        "tester_email": st.session_state.get("user_email"),
        "tester_name": st.session_state.get("tester_name"),
        "evaluation_timestamp": datetime.utcnow().isoformat(),
        "current_question": st.session_state.get("current_evaluation_question"),
        "current_industry": st.session_state.get("current_evaluation_industry"),
        "ratings": {}
    }
    
    # Collect ratings for each response (A, B, C, D)
    for response_id in ["A", "B", "C", "D"]:
        rating_key = f"ratings_{response_id}"
        if rating_key in st.session_state:
            evaluation_data["ratings"][response_id] = st.session_state[rating_key]
    
    return evaluation_data

def collect_final_evaluation_data() -> Dict:
    """
    Collect final evaluation data including overall feedback.
    
    Returns:
        Dictionary containing final evaluation data
    """
    # Get evaluation session data
    session = st.session_state.get("evaluation_session", {})
    completed_questions = session.get("completed_questions", set())
    selected_questions = session.get("selected_questions", {})
    
    # Count completed questions
    retail_count = len([q for q in completed_questions if q.startswith("retail:")])
    finance_count = len([q for q in completed_questions if q.startswith("finance:")])
    total_count = retail_count + finance_count
    
    # Get final feedback
    final_feedback = st.session_state.get("final_feedback", {})
    
    evaluation_data = {
        "tester_email": st.session_state.get("user_email"),
        "tester_name": st.session_state.get("tester_name"),
        "evaluation_timestamp": datetime.utcnow().isoformat(),
        "evaluation_type": "final_assessment",
        "questions_evaluated": {
            "retail_count": retail_count,
            "finance_count": finance_count,
            "total_count": total_count,
            "completed_questions": list(completed_questions)
        },
        "overall_ratings": {
            "overall_quality": final_feedback.get("overall_quality", 0),
            "overall_relevance": final_feedback.get("overall_relevance", 0),
            "overall_accuracy": final_feedback.get("overall_accuracy", 0),
            "overall_usefulness": final_feedback.get("overall_usefulness", 0)
        },
        "detailed_feedback": {
            "strengths": final_feedback.get("strengths", ""),
            "weaknesses": final_feedback.get("weaknesses", ""),
            "suggestions": final_feedback.get("suggestions", ""),
            "general_comments": final_feedback.get("general_comments", "")
        }
    }
    
    return evaluation_data

def save_evaluation_data(evaluation_data: Dict):
    """
    Save evaluation data to persistent storage using GCS.
    
    Args:
        evaluation_data: The evaluation data to save
    """
    try:
        # Use GCS data store
        from utils.data_store import DataStore
        
        data_store = DataStore("gcs")
        
        # Save evaluation data to GCS
        success = data_store.save_evaluation_data(evaluation_data)
        
        if success:
            st.success("✅ Evaluation submitted successfully to cloud storage!")
        else:
            st.error("❌ Failed to save evaluation to cloud storage")
            return
        
        # Mark evaluation as completed in registration
        mark_evaluation_completed(evaluation_data.get("tester_email"))
        
    except Exception as e:
        st.error(f"Error saving evaluation: {str(e)}")

def mark_evaluation_completed(email: str):
    """
    Mark a tester's evaluation as completed using GCS.
    
    Args:
        email: The tester's email address
    """
    try:
        from utils.data_store import DataStore
        
        # Use GCS data store
        data_store = DataStore("gcs")
        
        # Load registrations from GCS
        registrations = data_store.load_registration_data()
        
        if email in registrations:
            # Mark as completed
            registrations[email]["evaluation_completed"] = True
            registrations[email]["evaluation_completed_timestamp"] = datetime.utcnow().isoformat()
            
            # Save back to GCS
            success = data_store.save_registration_data(registrations[email])
            
            if success:
                st.success("✅ Evaluation completion status saved to cloud storage")
            else:
                st.error("❌ Failed to save completion status to cloud storage")
            
            # Also update session state if available
            if "tester_registrations" in st.session_state and email in st.session_state["tester_registrations"]:
                st.session_state["tester_registrations"][email]["evaluation_completed"] = True
                st.session_state["tester_registrations"][email]["evaluation_completed_timestamp"] = datetime.utcnow().isoformat()
                
    except Exception as e:
        st.error(f"Error marking evaluation as completed: {str(e)}")

def display_evaluation_progress(session: Dict):
    """Display progress through the evaluation."""
    st.markdown("### 📊 Evaluation Progress")
    
    # Progress bars
    col1, col2 = st.columns(2)
    
    with col1:
        retail_completed = len([q for q in session["completed_questions"] if q.startswith("retail:")])
        retail_total = len(session["selected_questions"].get("retail", []))
        retail_progress = retail_completed / retail_total if retail_total > 0 else 0
        st.progress(retail_progress)
        st.write(f"**Retail Industry**: {retail_completed}/{retail_total} questions completed")
    
    with col2:
        finance_completed = len([q for q in session["completed_questions"] if q.startswith("finance:")])
        finance_total = len(session["selected_questions"].get("finance", []))
        finance_progress = finance_completed / finance_total if finance_total > 0 else 0
        st.progress(finance_progress)
        st.write(f"**Finance Industry**: {finance_completed}/{finance_total} questions completed")
    
    # Current status
    current_industry = session["current_industry"]
    current_question_index = session["current_question_index"]
    current_total = len(session["selected_questions"].get(current_industry, []))
    
    if current_industry == "retail":
        st.info(f"🛒 Currently evaluating: **Retail Industry** (Question {current_question_index + 1}/{current_total})")
    else:
        st.info(f"💰 Currently evaluating: **Finance Industry** (Question {current_question_index + 1}/{current_total})")
    
    st.markdown("---")

def show_completion_message():
    """Show completion message and collect final feedback when all evaluations are done."""
    st.balloons()
    st.success("🎉 **Congratulations! You have completed all evaluations!**")
    
    # Get actual question counts
    selected_questions = st.session_state.get("evaluation_session", {}).get("selected_questions", {})
    retail_count = len(selected_questions.get("retail", []))
    finance_count = len(selected_questions.get("finance", []))
    total_count = retail_count + finance_count
    
    st.markdown(f"""
    ### 📋 Evaluation Summary
    
    You have successfully completed:
    - ✅ **{retail_count} Retail Industry questions**
    - ✅ **{finance_count} Finance Industry questions**
    - ✅ **Total: {total_count} questions evaluated**
    """)
    
    # Final Feedback Collection
    st.markdown("### 📝 Final Assessment Feedback")
    st.markdown("""
    Please provide your overall assessment of the AI model responses you evaluated. 
    This feedback will help us understand your general impressions and suggestions for improvement.
    """)
    
    # Overall ratings
    st.markdown("#### 📊 Overall Assessment Ratings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        overall_quality = st.selectbox(
            "Overall Quality of Responses",
            options=[1, 2, 3, 4, 5],
            help="Rate the overall quality of all AI responses you evaluated"
        )
        
        overall_relevance = st.selectbox(
            "Overall Relevance of Responses",
            options=[1, 2, 3, 4, 5],
            help="Rate how relevant the responses were to the business questions"
        )
    
    with col2:
        overall_accuracy = st.selectbox(
            "Overall Accuracy of Responses",
            options=[1, 2, 3, 4, 5],
            help="Rate the factual accuracy compared to ground truth data"
        )
        
        overall_usefulness = st.selectbox(
            "Overall Usefulness for Business",
            options=[1, 2, 3, 4, 5],
            help="Rate how useful these responses would be for business decision-making"
        )
    
    # Detailed feedback
    st.markdown("#### 💭 Detailed Feedback")
    
    strengths = st.text_area(
        "What were the strengths of the AI responses?",
        placeholder="Describe what worked well, what impressed you, or what was particularly helpful...",
        height=120
    )
    
    weaknesses = st.text_area(
        "What were the weaknesses or areas for improvement?",
        placeholder="Describe what could be better, what was confusing, or what was missing...",
        height=120
    )
    
    suggestions = st.text_area(
        "What suggestions do you have for improving AI business analysis?",
        placeholder="Share your ideas for how AI could better serve business intelligence needs...",
        height=120
    )
    
    general_comments = st.text_area(
        "Any additional comments or observations?",
        placeholder="Share any other thoughts about the evaluation experience or AI capabilities...",
        height=100
    )
    
    # Store final feedback in session state
    final_feedback = {
        "overall_quality": overall_quality,
        "overall_relevance": overall_relevance,
        "overall_accuracy": overall_accuracy,
        "overall_usefulness": overall_usefulness,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "general_comments": general_comments
    }
    
    st.session_state["final_feedback"] = final_feedback
    
    # Submit final feedback
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📤 Submit Final Assessment", type="primary", use_container_width=True):
            # Collect and save final evaluation data
            evaluation_data = collect_final_evaluation_data()
            save_evaluation_data(evaluation_data)
            
            # Mark evaluation as completed
            tester_email = st.session_state.get("user_email")
            if tester_email:
                mark_evaluation_completed(tester_email)
            
            st.success("✅ Final assessment submitted successfully!")
            st.markdown("""
            ### 📊 What Happens Next
            
            Your comprehensive evaluation has been saved and will be used for:
            - **Performance analysis** of different AI models
            - **Comparative research** between LLM providers
            - **Quality assessment** of business analysis capabilities
            - **Improvement recommendations** for AI business intelligence tools
            
            Thank you for your valuable contribution to this research!
            """)
            
            # Option to reset for testing (remove in production)
            if st.button("🔄 Reset Evaluation (Testing Only)", help="Reset evaluation session for testing"):
                if "evaluation_session" in st.session_state:
                    del st.session_state["evaluation_session"]
                if "final_feedback" in st.session_state:
                    del st.session_state["final_feedback"]
                st.rerun()

def show_evaluation_interface():
    """Main function to display the blind evaluation interface."""
    
    # Check if user is registered
    if not st.session_state.get("user_email"):
        st.error("❌ Please complete registration before participating in the evaluation.")
        return
    
    # Load evaluation data
    questions, responses = load_evaluation_data()
    
    if not questions or not responses:
        st.error("❌ Unable to load evaluation data. Please contact the administrator.")
        return
    
    # Page header
    st.title("🔍 Blind Evaluation")
    st.markdown("""
    Welcome to the blind evaluation! You will evaluate responses from different AI models 
    without knowing which model generated each response.
    
    **Evaluation Flow:**
    - You will complete **6 questions per industry**
    - Start with **Retail** industry, then move to **Finance**
    - Questions are randomly selected from a pool of 10 per industry
    """)
    
    # Display instructions
    with st.expander("📋 Evaluation Instructions", expanded=False):
        display_evaluation_instructions()
    
    # Display dataset overview
    with st.expander("📊 Dataset Overview", expanded=False):
        display_dataset_overview()
    
    # Initialize evaluation session state
    if "evaluation_session" not in st.session_state:
        st.session_state["evaluation_session"] = {
            "current_industry": "retail",
            "current_question_index": 0,
            "selected_questions": {},
            "completed_questions": set(),
            "industry_completed": {"retail": False, "finance": False}
        }
    
    # Get or generate selected questions for each industry
    if "selected_questions" not in st.session_state["evaluation_session"] or not st.session_state["evaluation_session"]["selected_questions"]:
        st.session_state["evaluation_session"]["selected_questions"] = {}
        for industry in questions.keys():
            # Get all questions for this industry
            all_questions = questions[industry]
            
            # Filter questions that have responses available
            questions_with_responses = []
            for question in all_questions:
                question_responses = get_responses_for_question(question, industry, responses)
                if len(question_responses) >= 2:  # Need at least 2 responses to evaluate
                    questions_with_responses.append(question)
            
            # Select questions (up to 6, or all available if less than 6)
            if questions_with_responses:
                selected = random.sample(questions_with_responses, min(6, len(questions_with_responses)))
                st.session_state["evaluation_session"]["selected_questions"][industry] = selected
            else:
                st.session_state["evaluation_session"]["selected_questions"][industry] = []
    
    # Get current evaluation state
    session = st.session_state["evaluation_session"]
    current_industry = session["current_industry"]
    current_question_index = session["current_question_index"]
    selected_questions = session["selected_questions"]
    completed_questions = session["completed_questions"]
    
    # Check if current industry is completed
    retail_total = len(selected_questions.get("retail", []))
    finance_total = len(selected_questions.get("finance", []))
    
    if current_industry == "retail" and len([q for q in completed_questions if q.startswith("retail:")]) >= retail_total:
        session["industry_completed"]["retail"] = True
        if finance_total > 0:
            session["current_industry"] = "finance"
            session["current_question_index"] = 0
            st.rerun()
        else:
            # No finance questions, evaluation complete
            show_completion_message()
            return
    
    if current_industry == "finance" and len([q for q in completed_questions if q.startswith("finance:")]) >= finance_total:
        session["industry_completed"]["finance"] = True
        # Both industries completed
        show_completion_message()
        return
    
    # Check if there are any questions available for current industry
    if not selected_questions.get(current_industry):
        st.warning(f"⚠️ No questions available for {current_industry} industry with responses.")
        if current_industry == "retail" and selected_questions.get("finance"):
            session["current_industry"] = "finance"
            session["current_question_index"] = 0
            st.rerun()
        elif current_industry == "finance":
            show_completion_message()
            return
        else:
            st.error("❌ No questions available for evaluation. Please contact the administrator.")
            return
    
    # Get current question
    if current_question_index >= len(selected_questions[current_industry]):
        # All questions for current industry completed
        session["industry_completed"][current_industry] = True
        if current_industry == "retail" and selected_questions.get("finance"):
            session["current_industry"] = "finance"
            session["current_question_index"] = 0
            st.rerun()
        else:
            show_completion_message()
            return
    
    current_question = selected_questions[current_industry][current_question_index]
    question_key = f"{current_industry}:{current_question}"
    
    # Check if this question is already completed
    if question_key in completed_questions:
        session["current_question_index"] += 1
        st.rerun()
    
    # Display progress
    display_evaluation_progress(session)
    
    # Get responses for current question
    question_responses = get_responses_for_question(current_question, current_industry, responses)
    
    if len(question_responses) < 4:
        st.warning(f"⚠️ Only {len(question_responses)} responses available for this question. Expected 4.")
    
    if question_responses:
        # Shuffle responses for anonymity
        shuffled_responses = shuffle_responses(question_responses)
        
        # Display question and responses
        question_count = len(selected_questions[current_industry])
        display_question_and_responses(current_question, current_industry, shuffled_responses, current_question_index + 1)
        
        # Submit button (collect individual ratings)
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("📤 Submit & Continue", type="primary", use_container_width=True):
                # Collect and save evaluation data
                evaluation_data = collect_evaluation_data()
                evaluation_data["question_key"] = question_key
                save_evaluation_data(evaluation_data)
                
                # Mark question as completed
                completed_questions.add(question_key)
                session["current_question_index"] += 1
                
                # Clear session state for next evaluation
                for key in list(st.session_state.keys()):
                    if key.startswith("ratings_") or key.startswith("quality_") or key.startswith("relevance_") or key.startswith("accuracy_") or key.startswith("uniformity_"):
                        del st.session_state[key]
                
                st.success("✅ Question submitted! Moving to next question...")
                st.rerun()
    else:
        st.error("❌ No responses available for the selected question.")

# Main execution
if __name__ == "__main__":
    show_evaluation_interface() 