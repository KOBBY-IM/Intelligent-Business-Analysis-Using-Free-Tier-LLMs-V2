"""
Tester Registration and Consent Management Module

This module handles:
- External tester registration with email and name collection
- Consent management with explicit opt-in requirements
- Email uniqueness validation to prevent duplicate registrations
- Secure PII handling and storage preparation
"""

import streamlit as st
import re
import json
import hashlib
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import logging
import os
REGISTRATION_FILE = os.path.join('data', 'registrations.json')

# Email validation regex pattern
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class RegistrationError(Exception):
    """Custom exception for registration-related errors"""
    pass

class ConsentError(Exception):
    """Custom exception for consent-related errors"""
    pass

def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex pattern.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email format is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Strip whitespace and convert to lowercase
    email = email.strip().lower()
    
    # Check basic format
    if not EMAIL_PATTERN.match(email):
        return False
    
    # Additional checks
    if len(email) > 254:  # RFC 5321 limit
        return False
    
    if '..' in email:  # Consecutive dots not allowed
        return False
    
    return True

def validate_name_format(name: str) -> bool:
    """
    Validate name format for registration.
    
    Args:
        name: Name to validate
    
    Returns:
        True if name format is valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    
    # Basic requirements
    if len(name) < 2:
        return False
    
    if len(name) > 100:
        return False
    
    # Must contain at least one letter
    if not any(c.isalpha() for c in name):
        return False
    
    # Check for reasonable characters (letters, spaces, hyphens, apostrophes)
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'.")
    if not all(c in allowed_chars for c in name):
        return False
    
    return True

def get_registration_storage_key() -> str:
    """
    Get the storage key for registration data.
    For now uses session state, but prepared for external storage.
    
    Returns:
        Storage key for registration data
    """
    return "tester_registrations"

def load_registrations_from_file() -> Dict[str, Dict]:
    """Load registrations from persistent file."""
    if not os.path.exists(REGISTRATION_FILE):
        return {}
    try:
        with open(REGISTRATION_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except Exception:
        return {}

def save_registrations_to_file(registrations: Dict[str, Dict]):
    """Save registrations to persistent file."""
    os.makedirs(os.path.dirname(REGISTRATION_FILE), exist_ok=True)
    with open(REGISTRATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(registrations, f, indent=2)

def get_registered_emails() -> List[str]:
    """
    Get list of already registered email addresses from both session and file.
    """
    storage_key = get_registration_storage_key()
    
    # Get emails from session state
    if storage_key not in st.session_state:
        st.session_state[storage_key] = {}
    
    session_emails = [email.lower() for email in st.session_state[storage_key].keys()]
    
    # Get emails from file
    file_regs = load_registrations_from_file()
    file_emails = [email.lower() for email in file_regs.keys()]
    
    # Combine both sources
    all_emails = set(session_emails + file_emails)
    return list(all_emails)

def store_registration(registration_record: Dict) -> bool:
    """
    Store a registration record securely in both session and file.
    """
    try:
        storage_key = get_registration_storage_key()
        email = registration_record["email"]
        
        # Initialize storage if needed
        if storage_key not in st.session_state:
            st.session_state[storage_key] = {}
        
        # Store in session state
        st.session_state[storage_key][email] = registration_record
        
        # Also update file
        regs = load_registrations_from_file()
        regs[email] = registration_record
        save_registrations_to_file(regs)
        
        # Log successful registration (without exposing PII)
        email_hash = hash_email_for_logging(email)
        logging.info(f"Registration stored for email hash: {email_hash}")
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to store registration: {str(e)}")
        return False

def is_email_already_registered(email: str) -> bool:
    """
    Check if an email address is already registered.
    
    Args:
        email: Email address to check
    
    Returns:
        True if email is already registered, False otherwise
    """
    if not email:
        return False
    
    email_normalized = email.strip().lower()
    registered_emails = get_registered_emails()
    
    return email_normalized in registered_emails

def has_email_completed_evaluation(email: str) -> bool:
    """
    Check if an email address has completed an evaluation.
    
    Args:
        email: Email address to check
    
    Returns:
        True if email has completed evaluation, False otherwise
    """
    if not email:
        return False
    
    email_normalized = email.strip().lower()
    
    # Check session state
    storage_key = get_registration_storage_key()
    if storage_key in st.session_state:
        session_reg = st.session_state[storage_key].get(email_normalized)
        if session_reg and session_reg.get("evaluation_completed", False):
            return True
    
    # Check file storage
    file_regs = load_registrations_from_file()
    file_reg = file_regs.get(email_normalized)
    if file_reg and file_reg.get("evaluation_completed", False):
        return True
    
    return False

def can_email_register(email: str) -> Tuple[bool, str]:
    """
    Check if an email can register for evaluation.
    
    Args:
        email: Email address to check
    
    Returns:
        Tuple of (can_register, reason)
    """
    if not email:
        return False, "Email is required"
    
    email_normalized = email.strip().lower()
    
    # Check if email has completed evaluation
    if has_email_completed_evaluation(email_normalized):
        return False, "This email address has already completed an evaluation. Only one evaluation per email is permitted."
    
    # Check if email is already registered but hasn't completed
    if is_email_already_registered(email_normalized):
        return True, "Email already registered but evaluation not completed. You can continue with your evaluation."
    
    return True, "Email can register for new evaluation."

def hash_email_for_logging(email: str) -> str:
    """
    Create a hash of email for secure logging purposes.
    
    Args:
        email: Email to hash
    
    Returns:
        SHA-256 hash of email (first 8 characters for logging)
    """
    if not email:
        return "NONE"
    
    email_hash = hashlib.sha256(email.encode()).hexdigest()
    return email_hash[:8]  # First 8 characters for logging

def create_registration_record(name: str, email: str, consent_given: bool) -> Dict:
    """
    Create a registration record with all required data.
    
    Args:
        name: Tester's name
        email: Tester's email
        consent_given: Whether consent was explicitly given
    
    Returns:
        Dictionary containing registration record
    """
    timestamp = datetime.utcnow().isoformat()
    
    return {
        "name": name.strip(),
        "email": email.strip().lower(),
        "consent_given": consent_given,
        "consent_timestamp": timestamp,
        "registration_timestamp": timestamp,
        "evaluation_completed": False,
        "session_id": st.session_state.get("user_role", "unknown")
    }



def get_registration_by_email(email: str) -> Optional[Dict]:
    """
    Retrieve registration record by email.
    
    Args:
        email: Email address to look up
    
    Returns:
        Registration record if found, None otherwise
    """
    if not email:
        return None
    
    email_normalized = email.strip().lower()
    storage_key = get_registration_storage_key()
    
    # Check session state first
    if storage_key in st.session_state:
        registrations = st.session_state[storage_key]
        if email_normalized in registrations:
            return registrations[email_normalized]
    
    # Check file storage
    file_regs = load_registrations_from_file()
    if email_normalized in file_regs:
        return file_regs[email_normalized]
    
    return None

def get_registration_stats() -> Dict:
    """
    Get statistics about registrations.
    
    Returns:
        Dictionary with registration statistics
    """
    storage_key = get_registration_storage_key()
    
    if storage_key not in st.session_state:
        return {
            "total_registrations": 0,
            "consented_registrations": 0,
            "completed_evaluations": 0
        }
    
    registrations = st.session_state[storage_key]
    
    total = len(registrations)
    consented = sum(1 for reg in registrations.values() if reg.get("consent_given", False))
    completed = sum(1 for reg in registrations.values() if reg.get("evaluation_completed", False))
    
    return {
        "total_registrations": total,
        "consented_registrations": consented,
        "completed_evaluations": completed
    }

def show_registration_form() -> Tuple[bool, Optional[Dict]]:
    """
    Display the tester registration form and handle submission.
    
    Returns:
        Tuple of (success, registration_record)
    """
    st.subheader("📝 Tester Registration")
    st.markdown("""
    Before participating in the evaluation, please provide your information and consent.
    
    **Your Privacy**: Your name and email will be securely stored and used solely for research purposes. 
    Only one evaluation per email address is permitted to ensure data integrity.
    """)
    
    with st.form("tester_registration_form"):
        # Name input
        name = st.text_input(
            "Full Name *",
            placeholder="Enter your full name",
            help="Your real name for research attribution"
        )
        
        # Email input
        email = st.text_input(
            "Email Address *",
            placeholder="Enter your email address",
            help="Must be a valid email address. Only one evaluation per email is allowed."
        )
        
        # Consent section
        st.markdown("### 📋 Consent to Participate")
        st.markdown("""
        **Research Purpose**: This evaluation compares the performance of different AI language models 
        for business analysis tasks in retail and finance industries.
        
        **Your Participation**: You will evaluate responses from 4 different AI models without knowing 
        which model generated each response.
        
        **Data Use**: Your ratings, comments, name, and email will be collected and analyzed for 
        research purposes. Data will be stored securely and used only for this academic study.
        
        **Rights**: You may withdraw from the study at any time. Your participation is voluntary.
        """)
        
        # Explicit consent checkbox
        consent_given = st.checkbox(
            "**I consent to participate in this research study**",
            help="You must provide explicit consent to participate"
        )
        
        # Additional confirmations
        email_confirmation = st.checkbox(
            "I confirm this is my actual email address and I understand only one evaluation per email is permitted"
        )
        
        # Submit button
        submitted = st.form_submit_button("Complete Registration", type="primary")
        
        if submitted:
            # Validation
            errors = []
            
            if not name:
                errors.append("Name is required")
            elif not validate_name_format(name):
                errors.append("Please enter a valid name (2-100 characters, letters and common punctuation only)")
            
            if not email:
                errors.append("Email is required")
            elif not validate_email_format(email):
                errors.append("Please enter a valid email address")
            else:
                # Check if email can register
                can_register, reason = can_email_register(email)
                if not can_register:
                    errors.append(reason)
                elif is_email_already_registered(email):
                    # Email is already registered but hasn't completed evaluation
                    st.info(f"ℹ️ {reason}")
                    # Allow them to continue with existing registration
                    existing_reg = get_registration_by_email(email)
                    if existing_reg:
                        st.session_state["tester_registered"] = True
                        st.session_state["tester_registration"] = existing_reg
                        st.success("✅ Welcome back! You can continue with your evaluation.")
                        return True, existing_reg
            
            if not consent_given:
                errors.append("You must provide explicit consent to participate")
            
            if not email_confirmation:
                errors.append("You must confirm your email address")
            
            # Display errors if any
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
                return False, None
            
            # Create registration record
            registration_record = create_registration_record(name, email, consent_given)
            
            # Store registration
            if store_registration(registration_record):
                st.success("✅ Registration completed successfully!")
                st.balloons()
                
                # Update session with registration info
                st.session_state["tester_registered"] = True
                st.session_state["tester_registration"] = registration_record
                
                return True, registration_record
            else:
                st.error("❌ Failed to complete registration. Please try again.")
                return False, None
    
    return False, None

def is_current_tester_registered() -> bool:
    """
    Check if the current tester is registered for evaluation.
    
    Returns:
        True if current tester is registered, False otherwise
    """
    return st.session_state.get("tester_registered", False)

def get_current_tester_registration() -> Optional[Dict]:
    """
    Get registration record for current tester.
    
    Returns:
        Registration record if available, None otherwise
    """
    return st.session_state.get("tester_registration")

def clear_current_registration():
    """Clear current tester registration from session."""
    if "tester_registered" in st.session_state:
        del st.session_state["tester_registered"]
    if "tester_registration" in st.session_state:
        del st.session_state["tester_registration"] 