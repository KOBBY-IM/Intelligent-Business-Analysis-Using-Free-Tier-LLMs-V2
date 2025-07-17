"""
Authentication and access control module for the LLM Evaluation System.

This module provides secure role-based authentication for:
- External testers (blind evaluation access)
- Administrators (full system access including analysis)
"""

import streamlit as st
import hashlib
from typing import Optional, Literal

# User roles
Role = Literal["tester", "admin", None]

class AuthenticationError(Exception):
    """Custom exception for authentication failures"""
    pass

def get_secret_safely(key_path: str) -> Optional[str]:
    """
    Safely retrieve a secret from Streamlit secrets.
    
    Args:
        key_path: Dot-separated path to the secret (e.g., 'auth.admin_password')
    
    Returns:
        Secret value or None if not found
    """
    try:
        keys = key_path.split('.')
        value = st.secrets
        for key in keys:
            value = value[key]
        return str(value) if value else None
    except (KeyError, AttributeError):
        return None

def hash_credential(credential: str) -> str:
    """
    Hash a credential for secure comparison.
    
    Args:
        credential: The credential to hash
    
    Returns:
        SHA-256 hash of the credential
    """
    return hashlib.sha256(credential.encode()).hexdigest()

def verify_tester_access(token: str) -> bool:
    """
    Verify external tester access token.
    
    Args:
        token: The access token provided by the tester
    
    Returns:
        True if token is valid, False otherwise
    """
    expected_token = get_secret_safely("auth.tester_access_token")
    if not expected_token:
        st.error("🔒 Tester access not configured. Please contact the administrator.")
        return False
    
    return token.strip() == expected_token.strip()

def verify_admin_access(password: str) -> bool:
    """
    Verify administrator password.
    
    Args:
        password: The password provided by the admin
    
    Returns:
        True if password is valid, False otherwise
    """
    expected_password = get_secret_safely("auth.admin_password")
    if not expected_password:
        st.error("🔒 Admin access not configured. Please contact the system administrator.")
        return False
    
    return password.strip() == expected_password.strip()

def get_current_user_role() -> Role:
    """
    Get the current user's role from session state.
    
    Returns:
        Current user role or None if not authenticated
    """
    return st.session_state.get("user_role", None)

def get_current_user_email() -> Optional[str]:
    """
    Get the current user's email from session state.
    
    Returns:
        Current user email or None if not available
    """
    return st.session_state.get("user_email", None)

def set_user_session(role: Role, email: Optional[str] = None):
    """
    Set user session data.
    
    Args:
        role: User role (tester, admin, or None)
        email: User email (for testers)
    """
    st.session_state["user_role"] = role
    st.session_state["user_email"] = email
    st.session_state["authenticated_at"] = st.session_state.get("authenticated_at", None)

def clear_user_session():
    """Clear all user session data."""
    # Clear authentication data
    for key in ["user_role", "user_email", "authenticated_at"]:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear registration data for testers
    for key in ["tester_registered", "tester_registration"]:
        if key in st.session_state:
            del st.session_state[key]

def require_role(required_role: Role) -> bool:
    """
    Check if current user has the required role.
    
    Args:
        required_role: The role required to access the resource
    
    Returns:
        True if user has required role, False otherwise
    """
    current_role = get_current_user_role()
    
    # Admin has access to everything
    if current_role == "admin":
        return True
    
    # Check specific role requirements
    if required_role == "tester" and current_role == "tester":
        return True
    
    return False

def show_tester_login() -> bool:
    """
    Display tester login form and handle authentication.
    
    Returns:
        True if authentication successful, False otherwise
    """
    st.subheader("🔐 External Tester Access")
    st.markdown("Please enter your access token to participate in the evaluation.")
    
    with st.form("tester_login"):
        access_token = st.text_input(
            "Access Token",
            type="password",
            placeholder="Enter your access token"
        )
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address"
        )
        
        col1, col2 = st.columns([1, 3])
        submitted = col1.form_submit_button("Access Evaluation")
        
        if submitted:
            if not access_token:
                st.error("❌ Please enter your access token.")
                return False
            
            if not email or "@" not in email:
                st.error("❌ Please enter a valid email address.")
                return False
            
            if verify_tester_access(access_token):
                set_user_session("tester", email)
                st.success("✅ Access granted! Welcome to the evaluation system.")
                st.rerun()
                return True
            else:
                st.error("❌ Invalid access token. Please check your credentials.")
                return False
    
    return False

def show_admin_login() -> bool:
    """
    Display admin login form and handle authentication.
    
    Returns:
        True if authentication successful, False otherwise
    """
    st.subheader("🔐 Administrator Access")
    st.markdown("Please enter your administrator password.")
    
    with st.form("admin_login"):
        password = st.text_input(
            "Administrator Password",
            type="password",
            placeholder="Enter administrator password"
        )
        
        col1, col2 = st.columns([1, 3])
        submitted = col1.form_submit_button("Access Admin Panel")
        
        if submitted:
            if not password:
                st.error("❌ Please enter your password.")
                return False
            
            if verify_admin_access(password):
                set_user_session("admin")
                st.success("✅ Administrator access granted!")
                st.rerun()
                return True
            else:
                st.error("❌ Invalid password. Access denied.")
                return False
    
    return False

def show_logout_button():
    """Display logout button and handle logout."""
    current_role = get_current_user_role()
    current_email = get_current_user_email()
    
    if current_role:
        st.sidebar.markdown("---")
        
        # Show current user info
        if current_role == "admin":
            st.sidebar.success("🔓 Logged in as Administrator")
        elif current_role == "tester":
            st.sidebar.success(f"🔓 Logged in as Tester")
            if current_email:
                st.sidebar.caption(f"Email: {current_email}")
        
        # Logout button
        if st.sidebar.button("🚪 Logout", type="secondary"):
            clear_user_session()
            st.rerun()

def enforce_page_access(page_name: str, required_role: Role = None) -> bool:
    """
    Enforce access control for a specific page.
    
    Args:
        page_name: Name of the page being accessed
        required_role: Role required to access the page
    
    Returns:
        True if access granted, False if access denied
    """
    current_role = get_current_user_role()
    
    # Public pages (no authentication required)
    public_pages = ["Home", "System Status"]
    if page_name in public_pages:
        return True
    
    # Check role-specific access
    if required_role and not require_role(required_role):
        st.error(f"🔒 Access Denied: {page_name}")
        st.markdown(f"You need **{required_role}** privileges to access this page.")
        
        # Show appropriate login form
        if required_role == "tester" and current_role != "admin":
            show_tester_login()
        elif required_role == "admin" and current_role != "admin":
            show_admin_login()
        
        return False
    
    return True 