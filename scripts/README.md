# Scripts Directory

This folder contains utility scripts for setup, configuration, and maintenance of the LLM evaluation system.

## Setup Scripts
- `setup_gcs.py` - Google Cloud Storage setup and configuration
- `setup_gcs.sh` - Shell script for GCS setup automation
- `configure_gcs.py` - GCS configuration and credential management

## Diagnostic Scripts
- `check_bucket.py` - Verify GCS bucket accessibility and permissions
- `check_gcs_data.py` - Inspect and validate data in GCS storage

## Usage

### Initial Setup
```bash
# Setup GCS integration
python scripts/setup_gcs.py

# Or use the shell script
bash scripts/setup_gcs.sh
```

### Diagnostics
```bash
# Check GCS connectivity
python scripts/check_bucket.py

# Validate stored data
python scripts/check_gcs_data.py
```

## Notes
- These scripts are for development and deployment setup
- They are not part of the main application runtime
- Ensure proper credentials are configured before running GCS scripts 