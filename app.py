import streamlit as st
import os
from datetime import datetime
from utils.auth import (
    get_current_user_role, 
    get_current_user_email,
    enforce_page_access, 
    show_logout_button,
    show_admin_login
)
from utils.registration import (
    show_registration_form,
    is_current_tester_registered,
    get_current_tester_registration,
    get_registration_stats,
    clear_current_registration
)

# Configure page settings
st.set_page_config(
    page_title="Intelligent Business Analysis - Free-Tier LLMs v2.1",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Initialize session state with default values"""
    # Initialize registration storage if not set
    if "tester_registrations" not in st.session_state:
        st.session_state["tester_registrations"] = {}
    
    # DO NOT initialize current_page here - let the navigation logic handle it
    # This ensures user's page selection persists across refreshes

def main():
    """Main application entry point"""
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title("🤖 Intelligent Business Analysis Using Free-Tier LLMs")
    st.caption("🔄 Version 2.1 - Enhanced Evaluation System")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Get current user role for dynamic navigation
    current_role = get_current_user_role()
    
    # Build navigation options based on user role
    nav_options = ["Home", "RAG Demo"]
    
    # Add role-specific pages
    if current_role == "tester" or current_role == "admin":
        nav_options.insert(-1, "Blind Evaluation")
    
    if current_role == "admin":
        nav_options.insert(-1, "Analysis Dashboard")
        nav_options.insert(-1, "Admin Panel")
        # Add direct access to analysis pages for admins
        nav_options.extend(["Blind Evaluation Analysis", "Technical Metrics Analysis", "Provider Comparison Analysis"])
    
    # If not authenticated, show admin login option only
    if not current_role:
        nav_options.append("Admin Login")
    
    # Determine default page based on user role and session state
    current_page_in_session = st.session_state.get("current_page")
    
    if current_role == "tester":
        # For testers, ensure they're not on login pages or invalid pages
        if (not current_page_in_session or 
            current_page_in_session in ["Admin Login"] or 
            current_page_in_session not in nav_options):
            default_page = "Blind Evaluation"
        else:
            default_page = current_page_in_session
    elif current_role == "admin":
        # For admins, ensure they're not on login pages or invalid pages  
        if (not current_page_in_session or 
            current_page_in_session in ["Admin Login"] or 
            current_page_in_session not in nav_options):
            default_page = "Analysis Dashboard"
        else:
            default_page = current_page_in_session
    else:
        # For unauthenticated users - default to Blind Evaluation for easier access
        if not current_page_in_session or current_page_in_session not in nav_options:
            default_page = "Blind Evaluation"  # Changed from nav_options[0] to "Blind Evaluation"
        else:
            default_page = current_page_in_session
    
    # Ensure the default page is in available options
    if default_page not in nav_options:
        default_page = nav_options[0]
    
    page = st.sidebar.selectbox("Select Page", nav_options, index=nav_options.index(default_page))
    
    # Store the current page selection in session state
    st.session_state["current_page"] = page
    
    # Show logout button if authenticated
    show_logout_button()
    
    # Route to appropriate page with access control
    if page == "Home":
        show_home()
    elif page == "Admin Login":
        show_admin_login_page()
    elif page == "Blind Evaluation":
        if enforce_page_access("Blind Evaluation", "tester"):
            # Redirect directly to the blind evaluation Streamlit page
            st.switch_page("pages/blind_evaluation.py")
    elif page == "Analysis Dashboard":
        if enforce_page_access("Analysis Dashboard", "admin"):
            show_analysis_dashboard()
    elif page == "Admin Panel":
        if enforce_page_access("Admin Panel", "admin"):
            show_admin_panel()
    elif page == "Blind Evaluation Analysis":
        if enforce_page_access("Blind Evaluation Analysis", "admin"):
            st.switch_page("pages/blind_evaluation_analysis.py")
    elif page == "Technical Metrics Analysis":
        if enforce_page_access("Technical Metrics Analysis", "admin"):
            st.switch_page("pages/technical_metrics_analysis.py")
    elif page == "Provider Comparison Analysis":
        if enforce_page_access("Provider Comparison Analysis", "admin"):
            st.switch_page("pages/provider_comparison.py")
    elif page == "RAG Demo":
        st.switch_page("pages/rag_demo.py")
    else:
        st.info(f"📋 {page} - Under Development")
        st.markdown("This page will be implemented in upcoming releases.")

def show_home():
    """Display the home page with comprehensive project information"""
    
    # Project introduction
    st.markdown("""
    ## 🎯 Welcome to the Intelligent Business Analysis Research Platform
    
    This research platform provides a comprehensive framework for evaluating and comparing free-tier 
    Large Language Models (LLMs) in business intelligence applications, specifically focusing on 
    **retail and finance industries**.
    """)
    
    # Main project description
    st.markdown("""
    ## 📋 Research Overview
    
    Organizations increasingly rely on AI-powered analysis for critical business decisions, yet selecting 
    the optimal LLM provider remains challenging due to limited comparative research and evidence-based 
    guidance. This study addresses this gap by providing systematic evaluation of free-tier LLMs through 
    both human assessment and automated technical metrics.
    """)
    
    # Two-column layout for key information
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
        ### 🔬 Research Methodology
        
        **Dual Evaluation Approach:**
        - **Human Blind Evaluation**: External testers evaluate AI responses without knowing 
          which model generated each answer
        - **Automated Technical Assessment**: Continuous monitoring of latency, throughput, 
          and reliability metrics
        
        **Retrieval-Augmented Generation (RAG):**
        - Responses grounded in real business datasets
        - Context-driven answer generation for improved relevance
        - Industry-specific knowledge base integration
        
        **Data-Driven Insights:**
        - Real e-commerce shopping trends dataset (3,900+ records)
        - Tesla stock market analysis data (2010-2025)
        - Comprehensive business scenarios and use cases
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Key Features
        
        **LLM Providers Evaluated:**
        - **Groq**: High-speed inference optimization
        - **OpenRouter**: Multi-model access platform
        - **Four distinct models** selected for comprehensive comparison
        
        **Evaluation Focus Areas:**
        - Response quality and clarity
        - Factual accuracy vs. ground truth
        - Business relevance and actionability
        - Consistency and organization
        
        **Target Industries:**
        - **Retail**: Customer behavior, sales analysis, inventory insights
        - **Finance**: Market trends, risk assessment, investment analysis
        """)
    
    # Call to action section
    st.markdown("---")
    
    cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
    
    with cta_col2:
        st.markdown("""
        ### 🚀 Participate in the Research
        
        **For External Evaluators:**
        Your participation helps advance AI evaluation methodologies and provides organizations 
        with evidence-based guidance for LLM selection in business contexts.
        
        **Time Commitment:** 20-30 minutes  
        **Evaluation Process:** Blind comparison of AI responses to business questions  
        **Impact:** Contribute to research that guides real-world AI adoption decisions  
        """)
        
        if st.button("🔍 Start Blind Evaluation", type="primary", use_container_width=True):
            st.session_state["current_page"] = "Blind Evaluation"
            st.switch_page("pages/blind_evaluation.py")
    
    # Research significance
    st.markdown("---")
    st.markdown("""
    ## 🎓 Research Significance
    
    This study contributes to the growing field of AI evaluation by:
    
    - **Advancing Evaluation Methodologies**: Combining human judgment with automated metrics 
      for comprehensive LLM assessment
    - **Industry-Specific Insights**: Providing targeted evaluation for business intelligence applications
    - **Open Research**: Transparent methodology and findings to benefit the broader research community
    - **Practical Applications**: Direct relevance for organizations making AI adoption decisions
    
    ### 📊 Expected Outcomes
    
    - **Comparative Performance Rankings** of free-tier LLMs in business contexts
    - **Best Practice Recommendations** for LLM selection and implementation  
    - **Evaluation Framework** that can be applied to future LLM assessments
    - **Open Dataset** of business-focused LLM evaluation results
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
    🎓 <strong>Academic Research Project</strong> | 
    Advancing AI Evaluation for Business Intelligence | 
    Your participation contributes to open research
    </div>
    """, unsafe_allow_html=True)



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
    """Display the blind evaluation page for testers"""
    
    # Import and run the blind evaluation page directly
    try:
        from pages.blind_evaluation import show_evaluation_interface
        show_evaluation_interface()
    except ImportError:
        st.error("❌ Blind evaluation interface not available. Please contact the administrator.")
    except Exception as e:
        st.error(f"❌ Error loading evaluation interface: {str(e)}")
        st.error(f"Debug: {type(e).__name__}: {str(e)}")

def show_analysis_dashboard():
    """Display the analysis dashboard for administrators"""
    st.header("📊 Analysis Dashboard")
    
    st.markdown("""
    ### Analysis Tools Overview
    
    This dashboard provides access to comprehensive analysis tools for LLM evaluation:
    """)
    
    # Analysis options with links to dedicated pages
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Blind Evaluation Analysis")
        st.markdown("""
        **Human Evaluation Data Analysis**
        - Statistical analysis with confidence intervals
        - Multi-dimensional LLM performance comparison
        - Rating distributions and significance testing
        - Qualitative feedback analysis
        """)
        if st.button("🔍 View Blind Evaluation Analysis", key="blind_analysis_btn"):
            st.switch_page("pages/blind_evaluation_analysis.py")
    
    with col2:
        st.subheader("⚡ Technical Metrics Analysis")
        st.markdown("""
        **Automated Performance Analysis**
        - Performance metrics over time
        - Latency, throughput, and reliability analysis
        - Failure analysis and rate limit detection
        - Industry-specific performance comparisons
        """)
        if st.button("📈 View Technical Metrics Analysis", key="tech_analysis_btn"):
            st.switch_page("pages/technical_metrics_analysis.py")
    
    st.markdown("---")
    
    # Quick access to other analysis tools
    st.subheader("🚀 Quick Access")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 Analysis Hub", key="hub_btn"):
            st.switch_page("pages/analysis.py")
    
    with col2:
        if st.button("🔍 LLM Health Check", key="health_btn"):
            st.switch_page("pages/llm_health_check.py")
    
    with col3:
        if st.button("📊 All Analysis Pages", key="all_btn"):
            st.info("Use the 'app' navigation in the sidebar to access all analysis pages")
    
    st.markdown("---")
    st.info("💡 **Tip**: Use the 'app' section in the sidebar for direct access to all analysis pages.")

def show_admin_panel():
    """Display the admin panel for system management"""
    st.header("⚙️ Administrator Panel")
    
    st.markdown("""
    ### System Management & Configuration
    
    Administrative tools for managing the LLM evaluation system.
    """)
    
    # Registration Statistics Section
    st.subheader("📊 Registration Statistics")
    
    stats = get_registration_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Registrations", stats["total_registrations"])
    with col2:
        st.metric("Consented Testers", stats["consented_registrations"])
    with col3:
        st.metric("Completed Evaluations", stats["completed_evaluations"])
    
    # Registration Management
    with st.expander("👥 Registration Management"):
        st.markdown("**Registered Testers Overview**")
        
        # Get registration data
        storage_key = "tester_registrations"
        if storage_key in st.session_state and st.session_state[storage_key]:
            registrations = st.session_state[storage_key]
            
            # Display registrations in a table format
            registration_data = []
            for email, reg in registrations.items():
                registration_data.append({
                    "Name": reg.get("name", "N/A"),
                    "Email": email,
                    "Consent": "✅" if reg.get("consent_given", False) else "❌",
                    "Registered": reg.get("registration_timestamp", "")[:19].replace("T", " "),
                    "Evaluation Complete": "✅" if reg.get("evaluation_completed", False) else "❌"
                })
            
            if registration_data:
                import pandas as pd
                df = pd.DataFrame(registration_data)
                st.dataframe(df, use_container_width=True)
                
                # Export functionality
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Registration Data (CSV)",
                    data=csv,
                    file_name=f"tester_registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No registrations found.")
        else:
            st.info("No registration data available.")
    
    # Admin sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 System Configuration")
        st.info("🚧 Configure LLM APIs and evaluation parameters")
        
        # Quick system actions
        st.markdown("**Quick Actions**")
        if st.button("🔄 Clear All Registration Data", type="secondary"):
            if st.checkbox("⚠️ I understand this will delete all registration data"):
                if "tester_registrations" in st.session_state:
                    del st.session_state["tester_registrations"]
                st.success("✅ Registration data cleared")
                st.rerun()
    
    with col2:
        st.subheader("📊 Data Management")
        st.info("🚧 Export evaluation data and manage storage")
        
        st.subheader("🔍 System Monitoring")
        st.info("🚧 Monitor system health and performance")
        
        # Storage information
        st.markdown("**Storage Status**")
        total_sessions = len(st.session_state.keys())
        st.write(f"Session state keys: {total_sessions}")
        
        if "tester_registrations" in st.session_state:
            reg_count = len(st.session_state["tester_registrations"])
            st.write(f"Stored registrations: {reg_count}")
        else:
            st.write("Stored registrations: 0")

if __name__ == "__main__":
    main() 