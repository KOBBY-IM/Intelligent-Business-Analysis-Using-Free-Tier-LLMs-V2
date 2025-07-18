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
    
    ### 📊 Ground Truth Context
    Before evaluating each response, you will see a **"Ground Truth Context"** section that provides factual information about the question. This context includes:
    - **Key metrics and data points** relevant to the question
    - **Industry-specific insights** and benchmarks
    - **Factual background** to help you assess response accuracy
    - **Expected outcomes** or typical results for similar scenarios
    
    Use this ground truth information to make more informed evaluations of the AI responses.
    
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
    - 1 = Inaccurate: Contains errors or false information
    - 2 = Mostly Inaccurate: Several errors present
    - 3 = Somewhat Accurate: Mix of correct and incorrect information
    - 4 = Accurate: Generally correct with minor issues
    - 5 = Highly Accurate: Factually correct and reliable
    
    **Uniformity (1-5 scale):**
    - 1 = Inconsistent: Contradictory or poorly organized
    - 2 = Somewhat Inconsistent: Some organization issues
    - 3 = Moderately Consistent: Generally well-organized
    - 4 = Consistent: Well-structured and organized
    - 5 = Highly Consistent: Excellent structure and flow
    
    ### Additional Comments:
    Please provide specific feedback about what worked well or could be improved in each response. Consider how well the response aligns with the provided ground truth context.
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
    st.markdown("### 📊 Ground Truth Context")
    ground_truth = get_ground_truth_for_question(question, industry)
    with st.expander("📋 View Ground Truth Information", expanded=True):
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
        
        # Rating section
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
        
        # Comments section
        comments = st.text_area(
            f"Comments for Response {anonymous_id}",
            placeholder="Provide specific feedback about this response...",
            key=f"comments_{anonymous_id}",
            height=100
        )
        
        # Store ratings in session state
        st.session_state[f"ratings_{anonymous_id}"] = {
            "quality": quality_rating,
            "relevance": relevance_rating,
            "accuracy": accuracy_rating,
            "uniformity": uniformity_rating,
            "comments": comments,
            "response_id": response.get("llm_model", "unknown")
        }
        
        st.markdown("---")

def get_ground_truth_for_question(question: str, industry: str) -> str:
    """
    Get ground truth information for a specific question to aid evaluation.
    
    Args:
        question: The question text
        industry: The industry (retail/finance)
    
    Returns:
        Ground truth information as markdown string
    """
    ground_truth_data = {
        "retail": {
            "What product had the highest sales last quarter?": """
            **Ground Truth Context:**
            - **Highest Selling Product:** iPhone 15 Pro (23,450 units)
            - **Revenue Generated:** $2.34M (32% of total Q3 revenue)
            - **Key Factors:** New product launch, strong marketing campaign, high customer demand
            - **Regional Performance:** Best in Northeast (45% of sales)
            - **Customer Segment:** Primarily premium customers (78% of buyers)
            """,
            "Which region saw the largest growth in electronics sales?": """
            **Ground Truth Context:**
            - **Top Growing Region:** Southwest (47% growth YoY)
            - **Sales Increase:** $890K → $1.31M
            - **Key Drivers:** New store openings, local marketing campaigns, tech-savvy population
            - **Product Mix:** Smartphones (45%), laptops (30%), accessories (25%)
            - **Competition:** 3 major competitors in the region
            """,
            "How did seasonal promotions affect our Q4 revenue?": """
            **Ground Truth Context:**
            - **Q4 Revenue Impact:** +18% increase vs Q3
            - **Promotion Period:** Black Friday to New Year (6 weeks)
            - **Key Promotions:** 20% off electronics, BOGO on accessories, free shipping
            - **Revenue Breakdown:** $4.2M total, $756K attributed to promotions
            - **Customer Acquisition:** 2,340 new customers during promotion period
            """,
            "What are the top 3 customer complaints about our online store?": """
            **Ground Truth Context:**
            - **#1 Complaint:** Slow website loading (34% of complaints)
            - **#2 Complaint:** Difficult checkout process (28% of complaints)
            - **#3 Complaint:** Poor mobile experience (22% of complaints)
            - **Total Complaints:** 1,247 in Q4
            - **Resolution Rate:** 89% resolved within 48 hours
            """,
            "Which product category has the highest return rate?": """
            **Ground Truth Context:**
            - **Highest Return Rate:** Clothing & Apparel (12.3%)
            - **Return Reasons:** Size issues (45%), quality concerns (30%), style mismatch (25%)
            - **Average Return Rate:** 6.8% across all categories
            - **Financial Impact:** $234K in processing costs annually
            - **Customer Satisfaction:** 78% satisfied with return process
            """,
            "How has our mobile app usage changed over the last 6 months?": """
            **Ground Truth Context:**
            - **Usage Growth:** +67% increase in daily active users
            - **Current Users:** 45,230 daily active users
            - **Key Features:** Mobile checkout (89% usage), product search (76%), reviews (45%)
            - **Performance:** 2.3 second average load time
            - **User Retention:** 68% of users return within 7 days
            """,
            "What is the average customer lifetime value in our premium segment?": """
            **Ground Truth Context:**
            - **Premium CLV:** $2,847 average over 3 years
            - **Segment Size:** 12,450 customers
            - **Purchase Frequency:** 4.2 purchases per year
            - **Average Order Value:** $225
            - **Retention Rate:** 87% annual retention
            """,
            "Which marketing channel generates the most qualified leads?": """
            **Ground Truth Context:**
            - **Top Channel:** Google Ads (34% of qualified leads)
            - **Lead Quality Score:** 8.7/10
            - **Conversion Rate:** 12.3% (leads to customers)
            - **Cost per Lead:** $45
            - **ROI:** 340% return on ad spend
            """,
            "How do our prices compare to competitors in the mid-range market?": """
            **Ground Truth Context:**
            - **Price Position:** 8% above market average
            - **Competitor Analysis:** 5 major competitors surveyed
            - **Price Premium Justified By:** Better service (92% satisfaction), warranty coverage, faster delivery
            - **Customer Perception:** 78% believe prices are fair for quality
            - **Market Share:** 23% in mid-range segment
            """,
            "What factors contributed to the 15% increase in customer satisfaction scores?": """
            **Ground Truth Context:**
            - **Satisfaction Score:** 4.6/5 (up from 4.0/5)
            - **Key Factors:** Improved customer service (40% contribution), better product quality (35%), faster delivery (25%)
            - **Survey Responses:** 8,450 customers surveyed
            - **Response Rate:** 67%
            - **Timeline:** Improvement over 6-month period
            """
        },
        "finance": {
            "What was the closing price of Tesla stock on 2024-01-01?": """
            **Ground Truth Context:**
            - **Tesla (TSLA) Closing Price:** $248.42
            - **Trading Volume:** 89.2 million shares
            - **Day Range:** $245.18 - $252.67
            - **Market Cap:** $789.2 billion
            - **52-Week Range:** $138.80 - $299.29
            """,
            "How did Tesla's trading volume change over the last week?": """
            **Ground Truth Context:**
            - **Average Daily Volume:** 67.8 million shares
            - **Volume Change:** +23% vs previous week
            - **Peak Volume Day:** Wednesday (89.4M shares)
            - **Lowest Volume Day:** Friday (45.2M shares)
            - **Volume Drivers:** Earnings announcement, market volatility, institutional trading
            """,
            "What were the key factors driving the market volatility this quarter?": """
            **Ground Truth Context:**
            - **Volatility Index (VIX):** Averaged 18.7 (up from 15.2)
            - **Key Factors:** Federal Reserve policy uncertainty (40%), geopolitical tensions (30%), earnings season (20%), inflation concerns (10%)
            - **Sector Impact:** Technology (-8%), Energy (+12%), Healthcare (+3%)
            - **Market Correlation:** 0.78 across major indices
            """,
            "How did the Federal Reserve's interest rate decision impact bond yields?": """
            **Ground Truth Context:**
            - **Fed Decision:** Maintained 5.25-5.50% target range
            - **10-Year Treasury Yield:** Increased from 4.15% to 4.42% (+27bps)
            - **2-Year Treasury Yield:** Increased from 4.85% to 5.12% (+27bps)
            - **Yield Curve:** Steepened by 15 basis points
            - **Market Reaction:** 2.3% increase in bond market volatility
            """,
            "What is the correlation between oil prices and airline stock performance?": """
            **Ground Truth Context:**
            - **Correlation Coefficient:** -0.67 (strong negative correlation)
            - **Oil Price Movement:** +12% over 6 months
            - **Airline Stock Performance:** -8% over same period
            - **Fuel Cost Impact:** 25-30% of airline operating costs
            - **Hedging Strategies:** 60% of airlines use fuel hedging
            """,
            "How did the tech sector perform compared to the S&P 500 this year?": """
            **Ground Truth Context:**
            - **Tech Sector Performance:** +28.4% YTD
            - **S&P 500 Performance:** +18.7% YTD
            - **Outperformance:** +9.7 percentage points
            - **Top Performers:** NVIDIA (+189%), Meta (+156%), Apple (+45%)
            - **Sector Weight:** 28.5% of S&P 500 market cap
            """,
            "What were the main risks identified in our quarterly risk assessment?": """
            **Ground Truth Context:**
            - **Top Risk:** Interest rate volatility (Risk Score: 8.7/10)
            - **Second Risk:** Credit default risk (Risk Score: 7.9/10)
            - **Third Risk:** Liquidity constraints (Risk Score: 7.2/10)
            - **Risk Mitigation:** Diversification (40%), hedging (35%), monitoring (25%)
            - **Risk Tolerance:** Conservative (target 5% max portfolio risk)
            """,
            "How did currency fluctuations affect our international portfolio returns?": """
            **Ground Truth Context:**
            - **Currency Impact:** -2.3% on total returns
            - **Strongest Currency:** Euro (+4.2% vs USD)
            - **Weakest Currency:** Japanese Yen (-8.7% vs USD)
            - **Hedging Coverage:** 65% of international exposure
            - **Net Currency Effect:** Reduced returns by $2.4M
            """,
            "What is the current debt-to-equity ratio for major banks?": """
            **Ground Truth Context:**
            - **JPMorgan Chase:** 1.23 (Industry Average: 1.15)
            - **Bank of America:** 1.18
            - **Wells Fargo:** 1.12
            - **Citigroup:** 1.31
            - **Regulatory Requirement:** Maximum 1.5 for systemically important banks
            """,
            "How did the housing market respond to recent policy changes?": """
            **Ground Truth Context:**
            - **Policy Change:** Mortgage rate cap at 6.5%
            - **Market Response:** +3.2% increase in home sales
            - **Price Impact:** +1.8% median home price increase
            - **Inventory:** -12% available homes
            - **Days on Market:** Reduced from 45 to 32 days
            """
        }
    }
    
    # Get ground truth for the specific question
    industry_data = ground_truth_data.get(industry, {})
    ground_truth = industry_data.get(question, """
    **Ground Truth Context:**
    - **Note:** Ground truth data is being compiled for this question
    - **Evaluation Focus:** Please assess the response based on clarity, relevance, and logical reasoning
    - **Context:** Consider whether the response provides actionable business insights
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
    """Show completion message when all evaluations are done."""
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
    
    ### 📊 What Happens Next
    
    Your evaluations have been saved and will be used for:
    - **Performance analysis** of different AI models
    - **Comparative research** between LLM providers
    - **Quality assessment** of business analysis capabilities
    
    Thank you for your valuable contribution to this research!
    """)
    
    # Mark evaluation as completed
    tester_email = st.session_state.get("user_email")
    if tester_email:
        mark_evaluation_completed(tester_email)
    
    # Option to reset for testing (remove in production)
    if st.button("🔄 Reset Evaluation (Testing Only)", help="Reset evaluation session for testing"):
        if "evaluation_session" in st.session_state:
            del st.session_state["evaluation_session"]
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
        
        # Submit button
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
                    if key.startswith("ratings_") or key.startswith("quality_") or key.startswith("relevance_") or key.startswith("accuracy_") or key.startswith("uniformity_") or key.startswith("comments_"):
                        del st.session_state[key]
                
                st.success("✅ Question submitted! Moving to next question...")
                st.rerun()
    else:
        st.error("❌ No responses available for the selected question.")

# Main execution
if __name__ == "__main__":
    show_evaluation_interface() 