import streamlit as st
import os
from datetime import datetime
from utils.auth import (
    get_current_user_role, 
    get_current_user_email,
    enforce_page_access, 
    show_logout_button,
    show_tester_login,
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
    
    # Determine default page based on user role and session state
    current_page_in_session = st.session_state.get("current_page")
    
    if current_role == "tester":
        # For testers, ensure they're not on login pages or invalid pages
        if (not current_page_in_session or 
            current_page_in_session in ["Tester Login", "Admin Login"] or 
            current_page_in_session not in nav_options):
            default_page = "Blind Evaluation"
        else:
            default_page = current_page_in_session
    elif current_role == "admin":
        # For admins, ensure they're not on login pages or invalid pages  
        if (not current_page_in_session or 
            current_page_in_session in ["Tester Login", "Admin Login"] or 
            current_page_in_session not in nav_options):
            default_page = "Analysis Dashboard"
        else:
            default_page = current_page_in_session
    else:
        # For unauthenticated users
        if not current_page_in_session or current_page_in_session not in nav_options:
            default_page = nav_options[0]  # Default to first available option
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
    
    # Enhanced secrets configuration check
    st.subheader("🔐 Secrets Configuration")
    if hasattr(st, 'secrets'):
        st.success("✅ Secrets management is available")
        
        # Debug: Check specific secrets (without exposing values)
        try:
            # Check if auth section exists
            if hasattr(st.secrets, 'auth'):
                st.success("✅ Auth section found in secrets")
                
                # Check individual auth secrets
                if hasattr(st.secrets.auth, 'admin_password'):
                    st.success("✅ Admin password configured")
                else:
                    st.error("❌ Admin password NOT configured in secrets")
                
                if hasattr(st.secrets.auth, 'tester_access_token'):
                    st.success("✅ Tester access token configured")
                else:
                    st.error("❌ Tester access token NOT configured in secrets")
            else:
                st.error("❌ Auth section NOT found in secrets")
                st.markdown("**You need to configure secrets in Streamlit Cloud dashboard**")
        except Exception as e:
            st.error(f"❌ Error checking secrets: {str(e)}")
            
        # Show available secret sections for debugging
        try:
            available_sections = list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else []
            if available_sections:
                st.info(f"📋 Available secret sections: {', '.join(available_sections)}")
            else:
                st.warning("⚠️ No secret sections found")
        except:
            st.warning("⚠️ Cannot enumerate secret sections")
    else:
        st.error("❌ Secrets management not available")
    
    # Deployment environment check
    st.subheader("☁️ Deployment Environment")
    if os.getenv('STREAMLIT_SHARING_MODE'):
        st.success("✅ Running on Streamlit Cloud")
        st.info("💡 Configure secrets in the Streamlit Cloud dashboard")
    else:
        st.info("🏠 Running locally - secrets loaded from .streamlit/secrets.toml")
    
    # Future API integration status (placeholder)
    st.subheader("🤖 LLM API Status")
    st.info("📋 LLM integrations will be configured in upcoming releases")
    
    # Memory and resource indicators
    st.subheader("💾 Session State Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Authentication Status:**")
        current_role = get_current_user_role()
        current_email = get_current_user_email()
        
        if current_role:
            st.success(f"✅ Logged in as: {current_role}")
            if current_email:
                st.info(f"📧 Email: {current_email}")
        else:
            st.info("ℹ️ Not authenticated")
        
        st.markdown("**Current Page:**")
        current_page = st.session_state.get("current_page", "Not set")
        st.info(f"📄 Page: {current_page}")
    
    with col2:
        st.markdown("**Registration Data:**")
        registrations = st.session_state.get("tester_registrations", {})
        st.info(f"👥 Registered testers: {len(registrations)}")
        
        st.markdown("**Session Keys:**")
        session_keys = list(st.session_state.keys())
        st.info(f"🔑 Active session keys: {len(session_keys)}")
        
        # Show session persistence info
        if st.checkbox("🔍 Show detailed session state", help="For debugging purposes"):
            with st.expander("Session State Details"):
                filtered_state = {k: v for k, v in st.session_state.items() 
                                if not k.startswith('_') and k != 'tester_registrations'}
                st.json(filtered_state)
    
    st.markdown("---")
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
    - **After successful login, you'll be automatically redirected to the evaluation page**
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
    
    # Check if current tester is registered
    if not is_current_tester_registered():
        # Show registration flow
        st.markdown("""
        ### Step 1: Registration Required
        
        Before you can participate in the blind evaluation, you need to complete a one-time registration 
        to provide your consent and ensure data integrity.
        """)
        
        success, registration_record = show_registration_form()
        
        if success:
            st.success("🎉 Registration complete! You may now proceed to the evaluation.")
            st.rerun()  # Refresh to show evaluation interface
        
        return  # Don't show evaluation interface until registered
    
    # If registered, show evaluation interface
    registration = get_current_tester_registration()
    
    if registration:
        # Store tester info in session state for the evaluation page
        st.session_state["tester_name"] = registration['name']
        st.session_state["tester_email"] = registration['email']
        
        # Welcome message with registration info
        st.success(f"Welcome back, {registration['name']}! Thank you for participating in our evaluation.")
        
        # Registration details
        with st.expander("📋 Your Registration Details"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {registration['name']}")
                st.write(f"**Email:** {registration['email']}")
            with col2:
                st.write(f"**Consent Given:** {'✅ Yes' if registration['consent_given'] else '❌ No'}")
                st.write(f"**Registered:** {registration['registration_timestamp'][:19].replace('T', ' ')}")
    
    # Import and run the blind evaluation page
    try:
        from pages.blind_evaluation import show_evaluation_interface
        show_evaluation_interface()
    except ImportError:
        st.error("❌ Blind evaluation interface not available. Please contact the administrator.")
    except Exception as e:
        st.error(f"❌ Error loading evaluation interface: {str(e)}")
        st.error(f"Debug: {type(e).__name__}: {str(e)}")
    
    # Debug: Clear registration button (for testing only - remove in production)
    if st.button("🔄 Reset Registration (Testing Only)", help="Clear current registration for testing"):
        clear_current_registration()
        st.rerun()

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