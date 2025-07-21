#!/usr/bin/env python3
"""
Debug Session State - Quick Test Script
Helps debug session state and navigation issues
"""

import streamlit as st

def debug_session_state():
    """Debug current session state"""
    st.write("## 🔍 Session State Debug")
    
    st.write("### Current Session State:")
    for key, value in st.session_state.items():
        if not key.startswith('_'):
            st.write(f"**{key}:** {value}")
    
    st.write("### Authentication Status:")
    user_role = st.session_state.get("user_role", "None")
    user_email = st.session_state.get("user_email", "None")
    current_page = st.session_state.get("current_page", "None")
    
    st.write(f"- **User Role:** {user_role}")
    st.write(f"- **User Email:** {user_email}")
    st.write(f"- **Current Page:** {current_page}")
    
    if st.button("Clear Session State"):
        st.session_state.clear()
        st.rerun()

if __name__ == "__main__":
    debug_session_state() 