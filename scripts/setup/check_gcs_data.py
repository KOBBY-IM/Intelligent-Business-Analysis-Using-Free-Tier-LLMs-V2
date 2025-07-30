"""
Check Google Cloud Storage Data

This script checks if data is being saved to GCS and verifies the data collection process.
"""

import streamlit as st
import json
from datetime import datetime

def check_gcs_data():
    """Check if data is being saved to GCS."""
    
    st.title("🔍 Check Google Cloud Storage Data")
    
    try:
        # Test data store
        from utils.data_store import DataStore
        
        st.write("**1. Testing DataStore initialization...**")
        data_store = DataStore("gcs")
        
        if data_store.storage_type == "gcs":
            st.success("✅ DataStore initialized with GCS")
        else:
            st.error(f"❌ DataStore using {data_store.storage_type} instead of GCS")
            return
        
        # Check storage status
        st.write("**2. Storage Status:**")
        status = data_store.get_storage_status()
        st.json(status)
        
        # Test saving sample data
        st.write("**3. Testing data save...**")
        
        sample_registration = {
            "name": "GCS Test User",
            "email": "gcs-test@example.com",
            "consent_given": True,
            "consent_timestamp": datetime.utcnow().isoformat(),
            "registration_timestamp": datetime.utcnow().isoformat(),
            "evaluation_completed": False,
            "session_id": "tester"
        }
        
        # Save registration
        success = data_store.save_registration_data(sample_registration)
        if success:
            st.success("✅ Registration data saved to GCS")
        else:
            st.error("❌ Failed to save registration data")
            return
        
        # Save evaluation data
        sample_evaluation = {
            "tester_email": "gcs-test@example.com",
            "tester_name": "GCS Test User",
            "evaluation_timestamp": datetime.utcnow().isoformat(),
            "current_question": "Test question for GCS",
            "current_industry": "retail",
            "question_key": "retail:test_question",
            "ratings": {
                "A": {
                    "quality": 4,
                    "relevance": 5,
                    "accuracy": 4,
                    "uniformity": 3,
                    "comments": "Test comment for GCS",
                    "response_id": "test-model"
                }
            }
        }
        
        success = data_store.save_evaluation_data(sample_evaluation)
        if success:
            st.success("✅ Evaluation data saved to GCS")
        else:
            st.error("❌ Failed to save evaluation data")
            return
        
        # Load and verify data
        st.write("**4. Loading data from GCS...**")
        
        # Load registrations
        registrations = data_store.load_registration_data()
        if registrations:
            st.success(f"✅ Loaded {len(registrations)} registration records from GCS")
            if "gcs-test@example.com" in registrations:
                st.write("**Sample registration from GCS:**")
                st.json(registrations["gcs-test@example.com"])
        else:
            st.error("❌ No registration data found in GCS")
        
        # Load evaluations
        evaluations = data_store.load_evaluation_data()
        if evaluations:
            st.success(f"✅ Loaded {len(evaluations)} evaluation records from GCS")
            
            # Find our test evaluation
            test_eval = None
            for eval_data in evaluations:
                if eval_data.get("tester_email") == "gcs-test@example.com":
                    test_eval = eval_data
                    break
            
            if test_eval:
                st.write("**Sample evaluation from GCS:**")
                st.json(test_eval)
            else:
                st.warning("⚠️ Test evaluation not found in loaded data")
        else:
            st.error("❌ No evaluation data found in GCS")
        
        st.success("🎉 GCS data check completed!")
        
    except Exception as e:
        st.error(f"❌ Error checking GCS data: {str(e)}")

if __name__ == "__main__":
    check_gcs_data() 