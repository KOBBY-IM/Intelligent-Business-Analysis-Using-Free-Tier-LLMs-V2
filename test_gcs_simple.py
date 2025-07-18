"""
Simple Google Cloud Storage Test

This script tests if GCS credentials are properly configured.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_gcs_credentials():
    """Test if GCS credentials are available."""
    
    print("🔍 Testing Google Cloud Storage Configuration...")
    
    try:
        # Test if we can import the required modules
        from google.cloud import storage
        from google.oauth2 import service_account
        print("✅ Google Cloud Storage libraries available")
        
        # Test if we can access Streamlit secrets
        import streamlit as st
        
        if "gcp_service_account" in st.secrets:
            print("✅ GCP service account found in secrets")
            
            # Try to create credentials
            service_account_info = st.secrets["gcp_service_account"]
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info
            )
            print("✅ Service account credentials created successfully")
            
            # Try to create storage client
            client = storage.Client(credentials=credentials)
            print("✅ Storage client created successfully")
            
            # Check bucket name
            bucket_name = st.secrets.get("gcs_bucket_name", "llm-eval-data-2025")
            print(f"✅ Bucket name configured: {bucket_name}")
            
            # Try to access bucket
            try:
                bucket = client.bucket(bucket_name)
                if bucket.exists():
                    print("✅ Bucket exists and is accessible")
                else:
                    print("⚠️  Bucket does not exist - you may need to create it")
            except Exception as e:
                print(f"⚠️  Could not access bucket: {str(e)}")
            
            return True
            
        else:
            print("❌ GCP service account not found in secrets")
            print("   Please add your service account JSON to .streamlit/secrets.toml")
            return False
            
    except ImportError as e:
        print(f"❌ Missing required libraries: {str(e)}")
        print("   Install with: pip install google-cloud-storage")
        return False
    except Exception as e:
        print(f"❌ Error testing GCS: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gcs_credentials()
    if success:
        print("\n🎉 Google Cloud Storage is properly configured!")
        print("   You can now use cloud storage for data persistence.")
    else:
        print("\n❌ Google Cloud Storage configuration needs attention.")
        print("   Please follow the setup instructions.") 