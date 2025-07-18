"""
Direct Google Cloud Storage Test

This script directly tests GCS connection without relying on Streamlit secrets.
"""

import json
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_gcs_direct():
    """Test GCS connection directly."""
    
    print("🔍 Testing Google Cloud Storage Connection Directly...")
    
    try:
        # Test if we can import the required modules
        from google.cloud import storage
        from google.oauth2 import service_account
        print("✅ Google Cloud Storage libraries available")
        
        # Load secrets directly from file
        secrets_file = ".streamlit/secrets.toml"
        if not os.path.exists(secrets_file):
            print(f"❌ Secrets file not found: {secrets_file}")
            return False
        
        print(f"✅ Found secrets file: {secrets_file}")
        
        # Read the secrets file
        with open(secrets_file, 'r') as f:
            secrets_content = f.read()
        
        # Extract the service account JSON
        if 'gcp_service_account = """' in secrets_content:
            start = secrets_content.find('gcp_service_account = """') + len('gcp_service_account = """')
            end = secrets_content.find('"""', start)
            service_account_json = secrets_content[start:end]
            
            print("✅ Found service account JSON in secrets")
            
            # Parse the JSON
            service_account_info = json.loads(service_account_json)
            print(f"✅ Service account for project: {service_account_info.get('project_id')}")
            print(f"✅ Client email: {service_account_info.get('client_email')}")
            
            # Create credentials
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info
            )
            print("✅ Service account credentials created successfully")
            
            # Create storage client
            client = storage.Client(credentials=credentials)
            print("✅ Storage client created successfully")
            
            # Get bucket name
            bucket_name = "llm-eval-data-2025"  # From your configuration
            print(f"✅ Using bucket: {bucket_name}")
            
            # Try to access bucket
            try:
                bucket = client.bucket(bucket_name)
                if bucket.exists():
                    print("✅ Bucket exists and is accessible")
                    
                    # Test basic operations
                    blob = bucket.blob("test-connection.txt")
                    blob.upload_from_string("Test connection successful", content_type="text/plain")
                    print("✅ Successfully uploaded test file")
                    
                    # Clean up test file
                    blob.delete()
                    print("✅ Successfully deleted test file")
                    
                    return True
                else:
                    print("⚠️  Bucket does not exist - you may need to create it")
                    print("   Go to: https://console.cloud.google.com/storage/browser")
                    print(f"   Create bucket: {bucket_name}")
                    return False
                    
            except Exception as e:
                print(f"⚠️  Could not access bucket: {str(e)}")
                return False
                
        else:
            print("❌ Service account JSON not found in secrets file")
            return False
            
    except ImportError as e:
        print(f"❌ Missing required libraries: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error testing GCS: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gcs_direct()
    if success:
        print("\n🎉 Google Cloud Storage is properly configured!")
        print("   You can now use cloud storage for data persistence.")
    else:
        print("\n❌ Google Cloud Storage configuration needs attention.")
        print("   Please check the error messages above.") 