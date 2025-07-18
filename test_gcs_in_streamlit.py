"""
Test Google Cloud Storage within Streamlit

This script tests GCS functionality in the Streamlit environment.
"""

import streamlit as st
import json
from datetime import datetime

def test_gcs_in_streamlit():
    """Test GCS functionality within Streamlit."""
    
    st.title("🧪 Google Cloud Storage Test")
    st.write("Testing data collection with Google Cloud Storage...")
    
    try:
        # Check if GCS credentials are available
        if "gcp_service_account" not in st.secrets:
            st.error("❌ GCP service account not found in secrets")
            return False
        
        st.success("✅ GCP service account found in secrets")
        
        # Check bucket name
        bucket_name = st.secrets.get("gcs_bucket_name", "llm-eval-data-2025")
        st.info(f"📦 Using bucket: {bucket_name}")
        
        # Test data store creation
        from utils.data_store import DataStore
        
        data_store = DataStore("gcs")
        
        if data_store.storage_type != "gcs":
            st.error("❌ Failed to initialize GCS data store")
            return False
        
        st.success("✅ GCS data store initialized successfully")
        
        # Test storage status
        status = data_store.get_storage_status()
        st.write("**Storage Status:**")
        st.json(status)
        
        # Test saving sample data
        st.write("**Testing data storage...**")
        
        sample_registration = {
            "name": "Streamlit Test User",
            "email": "streamlit-test@example.com",
            "consent_given": True,
            "consent_timestamp": datetime.utcnow().isoformat(),
            "registration_timestamp": datetime.utcnow().isoformat(),
            "evaluation_completed": False,
            "session_id": "tester"
        }
        
        success = data_store.save_registration_data(sample_registration)
        if success:
            st.success("✅ Registration data saved to GCS")
        else:
            st.error("❌ Failed to save registration data")
            return False
        
        # Test loading data
        st.write("**Testing data retrieval...**")
        
        loaded_registrations = data_store.load_registration_data()
        if loaded_registrations:
            st.success(f"✅ Retrieved {len(loaded_registrations)} registration records")
            
            # Show sample data
            if "streamlit-test@example.com" in loaded_registrations:
                st.write("**Sample Registration Data:**")
                st.json(loaded_registrations["streamlit-test@example.com"])
        else:
            st.error("❌ Failed to retrieve registration data")
            return False
        
        st.success("🎉 All GCS tests passed!")
        st.write("Your data collection system is ready for production use.")
        return True
        
    except Exception as e:
        st.error(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    test_gcs_in_streamlit() 