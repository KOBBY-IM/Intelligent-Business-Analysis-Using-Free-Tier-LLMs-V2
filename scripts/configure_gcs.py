"""
Google Cloud Storage Configuration Helper

This script helps you configure Google Cloud Storage for the LLM evaluation system.
"""

import json
import os
from pathlib import Path

def main():
    """Main configuration function."""
    
    print("🔧 Google Cloud Storage Configuration for LLM Evaluation System")
    print("=" * 60)
    
    print("\n📋 Prerequisites:")
    print("1. Google Cloud account with billing enabled")
    print("2. Google Cloud CLI installed (gcloud)")
    print("3. A project created in Google Cloud Console")
    
    print("\n🚀 Step-by-Step Setup:")
    print("\n1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    
    print("\n2. Create or select your project:")
    project_id = input("   Enter your Google Cloud Project ID: ").strip()
    
    print("\n3. Enable Cloud Storage API:")
    print("   - Go to APIs & Services > Library")
    print("   - Search for 'Cloud Storage'")
    print("   - Click 'Enable'")
    
    print("\n4. Create a Service Account:")
    print("   - Go to IAM & Admin > Service Accounts")
    print("   - Click 'Create Service Account'")
    print("   - Name: llm-evaluation-storage")
    print("   - Description: Service account for LLM evaluation data")
    print("   - Grant 'Storage Object Admin' role")
    
    print("\n5. Create and download the service account key:")
    print("   - Click on the created service account")
    print("   - Go to 'Keys' tab")
    print("   - Click 'Add Key' > 'Create new key'")
    print("   - Choose JSON format")
    print("   - Download the key file")
    
    print("\n6. Create a Cloud Storage bucket:")
    bucket_name = input("   Enter bucket name (e.g., llm-evaluation-data-2024): ").strip()
    
    print("\n7. Configure Streamlit secrets:")
    print("   - Open the downloaded service account JSON file")
    print("   - Copy the entire content")
    print("   - Replace the placeholder in .streamlit/secrets.toml")
    print("   - Update the bucket name in secrets.toml")
    
    # Create a template for the user
    template = f'''# Updated .streamlit/secrets.toml configuration
# LLM API Keys (to be configured)
[api_keys]
# groq_api_key = "your-groq-api-key"
# google_gemini_api_key = "your-gemini-api-key" 
# openrouter_api_key = "your-openrouter-api-key"

# Authentication Tokens
[auth]
admin_password = "Root_Blamlez"
tester_access_token = "EvalTester2025"

# Google Cloud Storage Configuration
# Replace this with your actual service account JSON content
gcp_service_account = """
{{
  "type": "service_account",
  "project_id": "{project_id}",
  "private_key_id": "YOUR_PRIVATE_KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY_CONTENT\\n-----END PRIVATE KEY-----\\n",
  "client_email": "llm-evaluation-storage@{project_id}.iam.gserviceaccount.com",
  "client_id": "YOUR_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/llm-evaluation-storage%40{project_id}.iam.gserviceaccount.com"
}}
"""

# Google Cloud Storage bucket name
gcs_bucket_name = "{bucket_name}"

# Google Drive folder ID (optional, for backup storage)
gdrive_folder_id = "your-google-drive-folder-id"
'''
    
    # Save the template
    with open('secrets_template_updated.toml', 'w') as f:
        f.write(template)
    
    print(f"\n✅ Template saved as 'secrets_template_updated.toml'")
    print(f"   Project ID: {project_id}")
    print(f"   Bucket name: {bucket_name}")
    
    print("\n🔧 Next Steps:")
    print("1. Copy your service account JSON content to .streamlit/secrets.toml")
    print("2. Update the bucket name in secrets.toml")
    print("3. Test the connection: python test_gcs_connection.py")
    print("4. Run the Streamlit app: streamlit run app.py")
    
    print("\n📝 Commands to run:")
    print(f"gcloud config set project {project_id}")
    print(f"gsutil mb -p {project_id} gs://{bucket_name}")
    print("python test_gcs_connection.py")

if __name__ == "__main__":
    main() 