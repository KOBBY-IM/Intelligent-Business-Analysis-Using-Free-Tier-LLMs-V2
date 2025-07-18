"""
Google Cloud Storage Setup Script

This script helps you set up and test Google Cloud Storage integration
for the LLM evaluation data collection system.
"""

import json
import os
import sys
from pathlib import Path

def create_gcs_bucket_script():
    """Create a script to set up GCS bucket and permissions."""
    
    script_content = '''#!/bin/bash
# Google Cloud Storage Setup Script
# Run this script to set up your GCS bucket and service account

echo "Setting up Google Cloud Storage for LLM Evaluation Data..."

# Set your project ID
PROJECT_ID="your-project-id-here"
BUCKET_NAME="llm-evaluation-data-2024"
SERVICE_ACCOUNT_NAME="llm-evaluation-storage"

echo "1. Setting project..."
gcloud config set project $PROJECT_ID

echo "2. Enabling Cloud Storage API..."
gcloud services enable storage.googleapis.com

echo "3. Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \\
    --display-name="LLM Evaluation Data Storage" \\
    --description="Service account for storing LLM evaluation data"

echo "4. Creating storage bucket..."
gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME

echo "5. Setting bucket permissions..."
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$BUCKET_NAME

echo "6. Creating and downloading service account key..."
gcloud iam service-accounts keys create service-account-key.json \\
    --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

echo "Setup complete!"
echo "Next steps:"
echo "1. Copy the contents of service-account-key.json to .streamlit/secrets.toml"
echo "2. Update the gcs_bucket_name in secrets.toml to: $BUCKET_NAME"
echo "3. Test the connection using: python test_gcs_connection.py"
'''
    
    with open('setup_gcs.sh', 'w') as f:
        f.write(script_content)
    
    print("Created setup_gcs.sh script")
    print("Make it executable with: chmod +x setup_gcs.sh")

def create_test_script():
    """Create a script to test GCS connection."""
    
    script_content = '''"""
Test Google Cloud Storage Connection

This script tests the GCS connection and data storage functionality.
"""

import json
import tempfile
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from utils.data_store import DataStore, create_data_store

def test_gcs_connection():
    """Test GCS connection and basic operations."""
    
    print("Testing Google Cloud Storage Connection...")
    
    try:
        # Create data store with GCS
        data_store = DataStore("gcs")
        
        if data_store.storage_type != "gcs":
            print("❌ Failed to initialize GCS. Check your credentials.")
            return False
        
        print("✅ GCS initialized successfully")
        
        # Test saving sample data
        sample_evaluation = {
            "tester_email": "test@example.com",
            "tester_name": "Test User",
            "evaluation_timestamp": "2024-01-01T00:00:00",
            "current_question": "Test question",
            "current_industry": "retail",
            "ratings": {
                "A": {
                    "quality": 4,
                    "relevance": 5,
                    "accuracy": 4,
                    "uniformity": 3,
                    "comments": "Test comment",
                    "response_id": "test-model"
                }
            }
        }
        
        # Save test data
        success = data_store.save_evaluation_data(sample_evaluation)
        if success:
            print("✅ Successfully saved evaluation data to GCS")
        else:
            print("❌ Failed to save evaluation data")
            return False
        
        # Load test data
        loaded_data = data_store.load_evaluation_data()
        if loaded_data:
            print("✅ Successfully loaded evaluation data from GCS")
            print(f"   Found {len(loaded_data)} evaluation records")
        else:
            print("❌ Failed to load evaluation data")
            return False
        
        # Test registration data
        sample_registration = {
            "name": "Test User",
            "email": "test@example.com",
            "consent_given": True,
            "consent_timestamp": "2024-01-01T00:00:00",
            "registration_timestamp": "2024-01-01T00:00:00",
            "evaluation_completed": False,
            "session_id": "test"
        }
        
        success = data_store.save_registration_data(sample_registration)
        if success:
            print("✅ Successfully saved registration data to GCS")
        else:
            print("❌ Failed to save registration data")
            return False
        
        # Load registration data
        loaded_registrations = data_store.load_registration_data()
        if loaded_registrations:
            print("✅ Successfully loaded registration data from GCS")
            print(f"   Found {len(loaded_registrations)} registration records")
        else:
            print("❌ Failed to load registration data")
            return False
        
        print("\\n🎉 All GCS tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing GCS: {str(e)}")
        return False

if __name__ == "__main__":
    test_gcs_connection()
'''
    
    with open('test_gcs_connection.py', 'w') as f:
        f.write(script_content)
    
    print("Created test_gcs_connection.py script")

def create_secrets_template():
    """Create a template for secrets configuration."""
    
    template_content = '''# Streamlit Secrets Configuration Template
# Replace the placeholder values with your actual GCS credentials

# Copy the entire content of your service account JSON file here
gcp_service_account = """
{
  "type": "service_account",
  "project_id": "YOUR_PROJECT_ID",
  "private_key_id": "YOUR_PRIVATE_KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY_CONTENT\\n-----END PRIVATE KEY-----\\n",
  "client_email": "YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com",
  "client_id": "YOUR_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/YOUR_SERVICE_ACCOUNT%40YOUR_PROJECT.iam.gserviceaccount.com"
}
"""

# Your GCS bucket name
gcs_bucket_name = "llm-evaluation-data-2024"

# Access control passphrases
tester_passphrase = "tester"
admin_passphrase = "admin123"

# Optional: Google Drive folder ID for backup storage
gdrive_folder_id = "YOUR_GOOGLE_DRIVE_FOLDER_ID"
'''
    
    with open('.streamlit/secrets_template.toml', 'w') as f:
        f.write(template_content)
    
    print("Created .streamlit/secrets_template.toml")

def main():
    """Main setup function."""
    
    print("Google Cloud Storage Setup for LLM Evaluation System")
    print("=" * 50)
    
    # Create .streamlit directory if it doesn't exist
    Path('.streamlit').mkdir(exist_ok=True)
    
    # Create setup files
    create_gcs_bucket_script()
    create_test_script()
    create_secrets_template()
    
    print("\\nSetup files created successfully!")
    print("\\nNext steps:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable Cloud Storage API")
    print("4. Create a service account with Storage Object Admin role")
    print("5. Download the service account JSON key")
    print("6. Copy the JSON content to .streamlit/secrets.toml")
    print("7. Update the bucket name in secrets.toml")
    print("8. Test the connection: python test_gcs_connection.py")
    print("\\nFor detailed instructions, see the generated setup_gcs.sh script")

if __name__ == "__main__":
    main() 