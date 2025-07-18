# Data Collection System for Human Evaluations

## Overview

This document describes the robust data collection mechanism implemented for securely collecting and storing human evaluation data in the LLM comparison system. The system supports multiple storage backends and ensures data integrity, security, and persistence.

## Architecture

### Core Components

1. **DataStore Class** (`utils/data_store.py`)
   - Main storage abstraction layer
   - Supports multiple storage backends
   - Handles data validation and serialization

2. **Storage Backends**
   - **Google Cloud Storage (GCS)**: Primary cloud storage solution
   - **Google Drive**: Alternative cloud storage
   - **Local File System**: Fallback for development/testing

3. **Data Validation**
   - Input validation for evaluation data
   - Input validation for registration data
   - Email format validation
   - Consent verification

4. **Security Features**
   - Secure credential management via Streamlit secrets
   - Data encryption in transit (HTTPS)
   - PII protection and logging
   - Access control mechanisms

## Data Schema

### Evaluation Data Structure

```json
{
  "tester_email": "user@example.com",
  "tester_name": "John Doe",
  "evaluation_timestamp": "2024-01-15T10:30:00Z",
  "current_question": "What product had the highest sales last quarter?",
  "current_industry": "retail",
  "question_key": "retail:question_1",
  "ratings": {
    "A": {
      "quality": 4,
      "relevance": 5,
      "accuracy": 4,
      "uniformity": 3,
      "comments": "Good response with clear insights",
      "response_id": "llama3-8b-8192"
    },
    "B": {
      "quality": 3,
      "relevance": 4,
      "accuracy": 3,
      "uniformity": 4,
      "comments": "Average response",
      "response_id": "gemini-1.5-flash"
    }
  }
}
```

### Registration Data Structure

```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "consent_given": true,
  "consent_timestamp": "2024-01-15T10:00:00Z",
  "registration_timestamp": "2024-01-15T10:00:00Z",
  "evaluation_completed": false,
  "session_id": "tester"
}
```

## Storage Backends

### 1. Google Cloud Storage (Recommended)

**Setup Instructions:**

1. Create a Google Cloud Project
2. Enable Cloud Storage API
3. Create a service account with Storage Object Admin role
4. Download the service account key JSON file
5. Configure Streamlit secrets:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
# ... other fields

gcs_bucket_name = "llm-evaluation-data"
```

**Features:**
- Automatic data versioning
- High availability and durability
- Built-in encryption
- Access control via IAM
- Cost-effective for large datasets

### 2. Google Drive

**Setup Instructions:**

1. Create a Google Drive folder for data storage
2. Get the folder ID from the URL
3. Configure Streamlit secrets:

```toml
gdrive_folder_id = "your-google-drive-folder-id"
```

**Features:**
- Easy setup and management
- Familiar interface
- Good for small to medium datasets
- Automatic backup

### 3. Local File System (Development)

**Features:**
- No external dependencies
- Fast for development
- Data stored in `data/` directory
- Automatic fallback when cloud storage unavailable

## Security Features

### 1. Credential Management

- All credentials stored in Streamlit secrets
- No hardcoded credentials in code
- Automatic fallback to local storage if credentials missing

### 2. Data Validation

- Email format validation
- Required field validation
- Consent verification
- Data type checking

### 3. PII Protection

- Email hashing for logging
- Secure data transmission
- Access control mechanisms
- Audit trail maintenance

### 4. Error Handling

- Graceful fallback mechanisms
- Comprehensive error logging
- User-friendly error messages
- Data integrity checks

## Data Persistence

### Incremental Storage

- New data is appended to existing files
- No data overwriting
- Automatic backup creation
- Version control for data files

### Data Formats

1. **JSON Format**: Primary storage format
   - Human-readable
   - Easy to process
   - Maintains data structure

2. **CSV Format**: Analysis-friendly format
   - Easy to import into analysis tools
   - Flat structure for statistical analysis
   - Compatible with pandas, Excel, etc.

### Backup Strategy

- Automatic backup creation
- Multiple storage locations
- Data redundancy
- Recovery procedures

## Testing Strategy

### Unit Tests

**Data Validation Tests:**
- Valid data acceptance
- Invalid data rejection
- Edge case handling
- Special character handling

**Storage Tests:**
- Save/load operations
- Data integrity verification
- Error handling
- Performance testing

### Integration Tests

**End-to-End Workflow:**
1. User registration
2. Evaluation completion
3. Data persistence verification
4. Data retrieval testing

**Edge Cases:**
- Very long comments
- Special characters in names/emails
- Empty fields
- Network failures
- Storage quota exceeded

### Security Tests

- Credential validation
- Data encryption verification
- Access control testing
- PII protection verification

## Deployment Instructions

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/test_data_store.py

# Run application
streamlit run app.py
```

### 2. Streamlit Cloud Deployment

1. **Configure Secrets:**
   - Go to Streamlit Cloud dashboard
   - Navigate to your app settings
   - Add secrets configuration

2. **Deploy Application:**
   - Connect GitHub repository
   - Set main file: `app.py`
   - Deploy application

3. **Verify Deployment:**
   - Test registration flow
   - Test evaluation submission
   - Verify data persistence
   - Check storage status

### 3. Cloud Storage Setup

**Google Cloud Storage:**
1. Create GCS bucket
2. Set up service account
3. Configure CORS if needed
4. Test connectivity

**Google Drive:**
1. Create shared folder
2. Set appropriate permissions
3. Get folder ID
4. Test access

## Monitoring and Maintenance

### Data Monitoring

- Storage usage tracking
- Data quality metrics
- Error rate monitoring
- Performance monitoring

### Maintenance Tasks

- Regular backup verification
- Storage cleanup
- Performance optimization
- Security updates

### Troubleshooting

**Common Issues:**
1. **Missing Credentials**: Check Streamlit secrets configuration
2. **Storage Quota**: Monitor storage usage
3. **Network Issues**: Check connectivity
4. **Data Corruption**: Verify data integrity

**Debugging:**
- Enable debug logging
- Check storage status
- Verify data validation
- Test storage connectivity

## Performance Considerations

### Optimization Strategies

1. **Batch Operations**: Group multiple saves
2. **Caching**: Cache frequently accessed data
3. **Compression**: Compress large datasets
4. **Indexing**: Index for fast retrieval

### Scalability

- Horizontal scaling support
- Load balancing
- Database migration path
- Performance monitoring

## Compliance and Privacy

### GDPR Compliance

- Data minimization
- Consent management
- Right to deletion
- Data portability

### Data Retention

- Automatic data retention policies
- Secure data deletion
- Audit trail maintenance
- Compliance reporting

## Future Enhancements

### Planned Features

1. **Real-time Analytics**: Live data visualization
2. **Advanced Security**: Multi-factor authentication
3. **Data Export**: Multiple format support
4. **API Integration**: REST API for data access

### Scalability Improvements

1. **Database Migration**: PostgreSQL integration
2. **Caching Layer**: Redis integration
3. **Load Balancing**: Multiple instance support
4. **CDN Integration**: Global data distribution

## Support and Documentation

### Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Data Privacy Guidelines](https://gdpr.eu/)

### Contact

For technical support or questions about the data collection system, please refer to the project documentation or create an issue in the repository. 