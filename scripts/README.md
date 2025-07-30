# Scripts

This directory contains utility scripts for setup, deployment, and maintenance.

## Directory Structure

### **Setup** (`setup/`)

Setup and configuration scripts:

- **`setup_gcs.py`** - Google Cloud Storage setup script
- **`setup_gcs.sh`** - GCS setup shell script
- **`configure_gcs.py`** - GCS configuration script

### **Deployment** (`deployment/`)

Deployment and maintenance scripts (to be added as needed).

## Script Categories

### **Infrastructure Setup**
- Google Cloud Storage configuration
- Environment setup
- Service account configuration
- Permission management

### **Deployment Scripts**
- Automated deployment procedures
- Environment validation
- Configuration management
- Health checks

### **Maintenance Scripts**
- Data backup procedures
- System monitoring
- Performance optimization
- Cleanup operations

## Usage

### **Setup Scripts**

```bash
# Run GCS setup
python3 scripts/setup/setup_gcs.py

# Run setup shell script
bash scripts/setup/setup_gcs.sh
```

### **Configuration Scripts**

```bash
# Configure GCS
python3 scripts/setup/configure_gcs.py
```

## Dependencies

- Google Cloud SDK
- Python 3.9+
- Required Python packages (see requirements.txt)

## Security

- Scripts handle sensitive configuration data
- Use environment variables for secrets
- Follow security best practices
- Validate permissions before execution

## Error Handling

All scripts include:
- Comprehensive error handling
- Logging and debugging output
- Rollback procedures
- Validation checks 