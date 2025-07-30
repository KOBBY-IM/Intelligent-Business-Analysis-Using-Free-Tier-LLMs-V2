"""
Check if Google Cloud Storage bucket exists
"""

import json
import os

def check_bucket():
    """Check if the GCS bucket exists."""
    
    print("🔍 Checking Google Cloud Storage bucket...")
    
    try:
        from google.cloud import storage
        from google.oauth2 import service_account
        
        # Load service account from secrets
        with open('.streamlit/secrets.toml', 'r') as f:
            content = f.read()
        
        # Extract service account JSON
        start = content.find('gcp_service_account = """') + len('gcp_service_account = """')
        end = content.find('"""', start)
        sa_json = content[start:end]
        sa_info = json.loads(sa_json)
        
        print(f"✅ Service account loaded for project: {sa_info['project_id']}")
        
        # Create client
        credentials = service_account.Credentials.from_service_account_info(sa_info)
        client = storage.Client(credentials=credentials)
        
        # Check bucket
        bucket_name = "llm-eval-data-2025"
        bucket = client.bucket(bucket_name)
        
        if bucket.exists():
            print(f"✅ Bucket '{bucket_name}' exists and is accessible")
            return True
        else:
            print(f"❌ Bucket '{bucket_name}' does not exist")
            print("   Please create it in Google Cloud Console:")
            print(f"   https://console.cloud.google.com/storage/browser?project={sa_info['project_id']}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    check_bucket() 