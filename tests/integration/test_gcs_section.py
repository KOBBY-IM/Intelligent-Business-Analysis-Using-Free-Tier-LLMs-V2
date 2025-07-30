"""
Test GCS with Section-based Secrets
"""

import streamlit as st
import json

def test_gcs_section():
    """Test GCS with the new section-based secrets structure."""
    
    st.title("🧪 GCS Test (Section-based Secrets)")
    
    try:
        # Check if GCS section exists
        if "gcs" not in st.secrets:
            st.error("❌ gcs section not found in secrets")
            return False
        
        st.success("✅ gcs section found in secrets")
        
        # Check for service account
        if "service_account" not in st.secrets["gcs"]:
            st.error("❌ service_account not found in gcs section")
            return False
        
        st.success("✅ service_account found in gcs section")
        
        # Get service account info
        service_account_info = st.secrets["gcs"]["service_account"]
        
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
        bucket_name = st.secrets["gcs"].get("bucket_name", "llm-eval-data-2025")
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
    success = test_gcs_section()
    if success:
        st.success("🎉 All GCS tests passed!")
    else:
        st.error("❌ Some tests failed") 