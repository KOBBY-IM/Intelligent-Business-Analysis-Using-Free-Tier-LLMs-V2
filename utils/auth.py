"""
Authentication and access control module for the LLM Evaluation System.

This module provides secure role-based authentication for:
- External testers (registration-based access)
- Administrators (password-based access)
"""

import streamlit as st
import hashlib
from typing import Optional, Literal
from datetime import datetime, timezone

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
    Set user session data after successful authentication.
    
    Args:
        role: User role (tester or admin)
        email: User email (for testers)
    """
    st.session_state["user_role"] = role
    if email:
        st.session_state["user_email"] = email
    st.session_state["login_timestamp"] = datetime.now(timezone.utc).isoformat()

def clear_user_session():
    """Clear user session data on logout."""
    keys_to_clear = ["user_role", "user_email", "login_timestamp"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def require_role(required_role: Role) -> bool:
    """
    Check if current user has the required role.
    
    Args:
        required_role: Role required to access the page
    
    Returns:
        True if user has required role, False otherwise
    """
    current_role = get_current_user_role()
    
    if not current_role:
        st.error("🔒 Authentication required. Please log in to access this page.")
        return False
    
    if current_role != required_role:
        st.error(f"🔒 Access denied. This page requires {required_role} privileges.")
        return False
    
    return True

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
                # Set the current page to Analysis Dashboard for admins
                st.session_state["current_page"] = "Analysis Dashboard"
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
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            clear_user_session()
            st.success("✅ Logged out successfully!")
            st.rerun()

def enforce_page_access(page_name: str, required_role: Role = None) -> bool:
    """
    Enforce access control for a specific page.
    
    Args:
        page_name: Name of the page being accessed
        required_role: Role required to access the page (None for any authenticated user)
    
    Returns:
        True if access is allowed, False otherwise
    """
    current_role = get_current_user_role()
    
    if not current_role:
        st.error(f"🔒 Authentication required to access {page_name}.")
        return False
    
    if required_role and current_role != required_role:
        st.error(f"🔒 Access denied. {page_name} requires {required_role} privileges.")
        return False
    
    return True 