import streamlit as st
import os
from utils.auth import (
    get_current_user_role, 
    enforce_page_access, 
    show_logout_button,
    show_tester_login,
    show_admin_login
)

# Configure page settings
st.set_page_config(
    page_title="Intelligent Business Analysis - Free-Tier LLMs",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
    # Header
    st.title("🤖 Intelligent Business Analysis Using Free-Tier LLMs")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Get current user role for dynamic navigation
    current_role = get_current_user_role()
    
    # Build navigation options based on user role
    nav_options = ["Home", "System Status"]
    
    # Add role-specific pages
    if current_role == "tester" or current_role == "admin":
        nav_options.insert(-1, "Blind Evaluation")
    
    if current_role == "admin":
        nav_options.insert(-1, "Analysis Dashboard")
        nav_options.insert(-1, "Admin Panel")
    
    # If not authenticated, show login options
    if not current_role:
        nav_options.extend(["Tester Login", "Admin Login"])
    
    page = st.sidebar.selectbox("Select Page", nav_options)
    
    # Show logout button if authenticated
    show_logout_button()
    
    # Route to appropriate page with access control
    if page == "Home":
        show_home()
    elif page == "System Status":
        show_system_status()
    elif page == "Tester Login":
        show_tester_login_page()
    elif page == "Admin Login":
        show_admin_login_page()
    elif page == "Blind Evaluation":
        if enforce_page_access("Blind Evaluation", "tester"):
            show_blind_evaluation()
    elif page == "Analysis Dashboard":
        if enforce_page_access("Analysis Dashboard", "admin"):
            show_analysis_dashboard()
    elif page == "Admin Panel":
        if enforce_page_access("Admin Panel", "admin"):
            show_admin_panel()
    else:
        st.info(f"📋 {page} - Under Development")
        st.markdown("This page will be implemented in upcoming releases.")

def show_home():
    """Display the home page with project overview"""
    
    st.header("📊 Project Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Objectives")
        st.markdown("""
        - **Compare 4 Free-Tier LLMs** from Groq, Google Gemini, and OpenRouter
        - **Implement RAG-based evaluation** with 70% context coverage
        - **Conduct blind human evaluations** by external testers
        - **Automated technical performance** monitoring
        - **Focus on Retail & Finance** business analysis
        """)
    
    with col2:
        st.subheader("🏗️ System Architecture")
        st.markdown("""
        - **Streamlit Cloud** deployment platform
        - **Modular RAG pipeline** for grounded responses
        - **Vector database** for efficient retrieval
        - **Secure access control** for different user roles
        - **Cloud-first design** principles
        """)
    
    st.header("🚀 Current Status")
    
    # Status indicators
    status_items = [
        ("Project Initialization", "✅", "Complete"),
        ("Streamlit Cloud Setup", "⏳", "In Progress"),
        ("LLM Integration", "📋", "Planned"),
        ("RAG Pipeline", "📋", "Planned"),
        ("Blind Evaluation System", "📋", "Planned"),
        ("Automated Monitoring", "📋", "Planned")
    ]
    
    for item, icon, status in status_items:
        col1, col2, col3 = st.columns([3, 1, 2])
        col1.write(f"{icon} {item}")
        col2.write(status)

def show_system_status():
    """Display system status and configuration check"""
    
    st.header("⚙️ System Status")
    
    # Environment checks
    st.subheader("🔧 Environment Configuration")
    
    # Check Python version
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    st.success(f"✅ Python Version: {python_version}")
    
    # Check Streamlit version
    st.success(f"✅ Streamlit Version: {st.__version__}")
    
    # Check secrets configuration (placeholder)
    st.subheader("🔐 Secrets Configuration")
    if hasattr(st, 'secrets'):
        st.info("🔧 Secrets management is available and ready for API key configuration")
    else:
        st.warning("⚠️ Secrets management not detected")
    
    # Deployment environment check
    st.subheader("☁️ Deployment Environment")
    if os.getenv('STREAMLIT_SHARING_MODE'):
        st.success("✅ Running on Streamlit Cloud")
    else:
        st.info("🏠 Running locally - Deploy to Streamlit Cloud for production")
    
    # Future API integration status (placeholder)
    st.subheader("🤖 LLM API Status")
    st.info("📋 LLM integrations will be configured in upcoming releases")
    
    # Memory and resource indicators
    st.subheader("💾 Resource Status")
    st.info("📊 Resource monitoring will be implemented for production deployment")

def show_tester_login_page():
    """Display tester login page"""
    st.header("🔐 External Tester Authentication")
    st.markdown("""
    Welcome to the Blind Evaluation System for Free-Tier LLM Comparison.
    
    **Important Information:**
    - You will evaluate responses from 4 different LLMs blindly (identities hidden)
    - Your email will be recorded for research purposes
    - Only one evaluation per email address is permitted
    - Your responses will help improve AI system selection for businesses
    """)
    
    st.markdown("---")
    show_tester_login()

def show_admin_login_page():
    """Display admin login page"""
    st.header("🔐 Administrator Authentication")
    st.markdown("""
    Administrator access provides full system control including:
    
    - **Analysis Dashboard**: View evaluation results and performance metrics
    - **Admin Panel**: Manage system configuration and user data
    - **System Monitoring**: Access technical performance data
    - **Data Export**: Download evaluation results and reports
    """)
    
    st.markdown("---")
    show_admin_login()

def show_blind_evaluation():
    """Display the blind evaluation page for authenticated testers"""
    st.header("🎯 Blind LLM Evaluation")
    
    # Welcome message with user info
    from utils.auth import get_current_user_email
    user_email = get_current_user_email()
    if user_email:
        st.success(f"Welcome, {user_email}! Thank you for participating in our evaluation.")
    
    st.markdown("""
    ### How the Evaluation Works
    
    1. **Anonymous Responses**: You'll see business analysis responses from 4 different LLMs
    2. **Blind Testing**: LLM identities are completely hidden during evaluation
    3. **Rate & Comment**: Provide ratings and qualitative feedback
    4. **One Session**: Complete evaluation in a single session
    
    **Evaluation Criteria:**
    - **Accuracy**: How correct and factual is the response?
    - **Relevance**: How well does it address the business question?
    - **Clarity**: How clear and understandable is the response?
    - **Actionability**: How useful is this for business decision-making?
    """)
    
    # Status indicator
    st.info("🚧 **Evaluation Interface**: Will be implemented in the next development phase")
    
    # Placeholder for future evaluation interface
    with st.expander("🔍 Preview: Future Evaluation Interface"):
        st.markdown("""
        ```
        Question 1: Retail Sales Analysis
        
        Response A: [LLM Response Hidden]
        Rate: ⭐⭐⭐⭐⭐ (1-5 stars)
        Comments: [Text area for feedback]
        
        Response B: [LLM Response Hidden]
        Rate: ⭐⭐⭐⭐⭐ (1-5 stars)
        Comments: [Text area for feedback]
        ```
        """)

def show_analysis_dashboard():
    """Display the analysis dashboard for administrators"""
    st.header("📊 Analysis Dashboard")
    
    st.markdown("""
    ### Evaluation Results Overview
    
    This dashboard provides comprehensive analysis of LLM performance based on:
    - **Human Evaluation Data**: Blind tester ratings and feedback
    - **Technical Performance Metrics**: Latency, throughput, reliability
    - **Comparative Analysis**: Side-by-side LLM performance comparison
    """)
    
    # Tabs for different analysis views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Performance Overview", 
        "👥 Human Evaluations", 
        "⚡ Technical Metrics", 
        "📋 Detailed Reports"
    ])
    
    with tab1:
        st.info("🚧 **Performance Overview**: Real-time LLM comparison charts will be displayed here")
        
    with tab2:
        st.info("🚧 **Human Evaluations**: Blind evaluation results and tester feedback analysis")
        
    with tab3:
        st.info("🚧 **Technical Metrics**: Automated performance monitoring results")
        
    with tab4:
        st.info("🚧 **Detailed Reports**: Downloadable analysis reports and data exports")

def show_admin_panel():
    """Display the admin panel for system management"""
    st.header("⚙️ Administrator Panel")
    
    st.markdown("""
    ### System Management & Configuration
    
    Administrative tools for managing the LLM evaluation system.
    """)
    
    # Admin sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 User Management")
        st.info("🚧 Manage tester accounts and evaluation sessions")
        
        st.subheader("🔧 System Configuration")
        st.info("🚧 Configure LLM APIs and evaluation parameters")
    
    with col2:
        st.subheader("📊 Data Management")
        st.info("🚧 Export evaluation data and manage storage")
        
        st.subheader("🔍 System Monitoring")
        st.info("🚧 Monitor system health and performance")

if __name__ == "__main__":
    main() 