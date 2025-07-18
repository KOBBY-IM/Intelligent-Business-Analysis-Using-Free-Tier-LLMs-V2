"""
Test GCS with Fixed Secrets Handling
"""

import streamlit as st
import json

def test_gcs_fixed():
    """Test GCS with the fixed secrets handling."""
    
    st.title("🧪 GCS Test (Fixed)")
    
    try:
        # Check if service account is available
        if "gcp_service_account" not in st.secrets:
            st.error("❌ gcp_service_account not found in secrets")
            return False
        
        st.success("✅ gcp_service_account found in secrets")
        
        # Get service account info
        service_account_info = st.secrets["gcp_service_account"]
        
        # Handle string format
        if isinstance(service_account_info, str):
            st.info("Parsing service account JSON string...")
            service_account_info = json.loads(service_account_info)
        
        st.success("✅ Service account JSON parsed successfully")
        
        # Test creating credentials
        from google.oauth2 import service_account
        from google.cloud import storage
        
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info
        )
        st.success("✅ Credentials created successfully")
        
        # Test creating client
        client = storage.Client(credentials=credentials)
        st.success("✅ Storage client created successfully")
        
        # Test bucket access
        bucket_name = st.secrets.get("gcs_bucket_name", "llm-eval-data-2025")
        bucket = client.bucket(bucket_name)
        
        if bucket.exists():
            st.success(f"✅ Bucket '{bucket_name}' exists and is accessible")
            
            # Test data store
            from utils.data_store import DataStore
            
            data_store = DataStore("gcs")
            if data_store.storage_type == "gcs":
                st.success("✅ DataStore initialized with GCS successfully")
                
                # Test storage status
                status = data_store.get_storage_status()
                st.write("**Storage Status:**")
                st.json(status)
                
                return True
            else:
                st.error("❌ DataStore failed to initialize with GCS")
                return False
        else:
            st.error(f"❌ Bucket '{bucket_name}' does not exist")
            return False
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gcs_fixed()
    if success:
        st.success("🎉 All GCS tests passed!")
    else:
        st.error("❌ Some tests failed") 