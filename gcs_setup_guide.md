# 🔧 GCS Configuration Guide for Streamlit Cloud

## Problem: "No batch evaluation data found" 

You have data in GCS but Streamlit Cloud can't access it due to authentication issues.

## ✅ Solution: Configure Streamlit Secrets

### 1. **Get Your Service Account Key**
```bash
# From your local setup that works with GCS
cat service-account-key.json
```

### 2. **Add to Streamlit Cloud Secrets**
Go to your Streamlit Cloud app → **"Manage app"** → **"Secrets"** → Add:

```toml
# Streamlit secrets configuration
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"

gcs_bucket_name = "llm-evaluation-data"
```

### 3. **Verify Data Access**
After adding secrets, your Technical Metrics Analysis page will show:
- ✅ "📊 Loaded X records from GCS (bucket: llm-evaluation-data)"
- ✅ Data last modified timestamp
- ✅ Full dashboard with your actual batch evaluation results

## 🎯 Expected Result

With proper GCS configuration, you'll see:
- **16.8 KB** batch_eval_metrics.csv data from GCS
- **44.1 KB** batch_eval_metrics.json data 
- Complete performance analysis of your 4 LLMs
- Real latency, throughput, and success rate metrics

## 🚀 Quick Test

After configuring secrets, the Technical Metrics Analysis page will automatically:
1. Connect to your GCS bucket
2. Load your actual batch evaluation data  
3. Display comprehensive performance dashboards
4. Show real metrics from your LLM evaluations

Your data exists - we just need to connect Streamlit Cloud to it! 📊
