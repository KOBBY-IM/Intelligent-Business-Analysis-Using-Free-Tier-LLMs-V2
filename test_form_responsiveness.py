#!/usr/bin/env python3
"""
Test script to verify form responsiveness in blind evaluation
"""

import streamlit as st
import json
import random

def test_form_responsiveness():
    """Test the form responsiveness with a simplified version"""
    
    st.title("🧪 Form Responsiveness Test")
    
    # Simulate the final feedback form
    with st.form("test_feedback_form", clear_on_submit=False):
        st.markdown("### 📝 Test Feedback Form")
        
        # Overall ratings
        col1, col2 = st.columns(2)
        
        with col1:
            overall_quality = st.selectbox(
                "Overall Quality",
                options=[1, 2, 3, 4, 5],
                key="test_quality"
            )
            
            overall_relevance = st.selectbox(
                "Overall Relevance",
                options=[1, 2, 3, 4, 5],
                key="test_relevance"
            )
        
        with col2:
            overall_accuracy = st.selectbox(
                "Overall Accuracy",
                options=[1, 2, 3, 4, 5],
                key="test_accuracy"
            )
            
            overall_usefulness = st.selectbox(
                "Overall Usefulness",
                options=[1, 2, 3, 4, 5],
                key="test_usefulness"
            )
        
        # Detailed feedback
        st.markdown("#### 💭 Detailed Feedback")
        
        strengths = st.text_area(
            "Strengths",
            placeholder="What were the strengths?",
            height=120,
            key="test_strengths"
        )
        
        weaknesses = st.text_area(
            "Weaknesses",
            placeholder="What were the weaknesses?",
            height=120,
            key="test_weaknesses"
        )
        
        suggestions = st.text_area(
            "Suggestions",
            placeholder="What suggestions do you have?",
            height=120,
            key="test_suggestions"
        )
        
        general_comments = st.text_area(
            "General Comments",
            placeholder="Any additional comments?",
            height=100,
            key="test_comments"
        )
        
        # Submit button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            submitted = st.form_submit_button("📤 Submit Test Feedback", type="primary", use_container_width=True)
        
        if submitted:
            # Store feedback
            feedback = {
                "overall_quality": overall_quality,
                "overall_relevance": overall_relevance,
                "overall_accuracy": overall_accuracy,
                "overall_usefulness": overall_usefulness,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": suggestions,
                "general_comments": general_comments
            }
            
            st.session_state["test_feedback"] = feedback
            st.success("✅ Test feedback submitted successfully!")
            st.json(feedback)

def main():
    """Main test function"""
    
    st.sidebar.title("🧪 Test Controls")
    
    if st.sidebar.button("Clear Session State"):
        keys_to_clear = ["test_feedback", "form_submitted"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.sidebar.success("Session state cleared!")
    
    if st.sidebar.button("Show Session State"):
        st.sidebar.json(st.session_state)
    
    test_form_responsiveness()
    
    # Show current feedback if exists
    if "test_feedback" in st.session_state:
        st.markdown("---")
        st.markdown("### 📊 Current Test Feedback")
        st.json(st.session_state["test_feedback"])

if __name__ == "__main__":
    main() 