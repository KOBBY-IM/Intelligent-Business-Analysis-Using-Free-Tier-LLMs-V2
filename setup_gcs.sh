#!/bin/bash
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
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="LLM Evaluation Data Storage" \
    --description="Service account for storing LLM evaluation data"

echo "4. Creating storage bucket..."
gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME

echo "5. Setting bucket permissions..."
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$BUCKET_NAME

echo "6. Creating and downloading service account key..."
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

echo "Setup complete!"
echo "Next steps:"
echo "1. Copy the contents of service-account-key.json to .streamlit/secrets.toml"
echo "2. Update the gcs_bucket_name in secrets.toml to: $BUCKET_NAME"
echo "3. Test the connection using: python test_gcs_connection.py"
