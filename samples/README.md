# Samples Directory

This folder contains scripts for generating sample data for testing and development purposes.

## Sample Data Generators

### Blind Evaluation Data
- `create_sample_blind_data.py` - Generates sample human evaluation responses
  - Creates realistic rating structures
  - Includes various tester scenarios
  - Useful for testing analysis pages

### Batch Evaluation Data  
- `create_sample_batch_data.py` - Generates sample technical metrics data
  - Creates performance measurement records
  - Includes latency, throughput, and error rate data
  - Useful for testing technical analysis features

### General Sample Data
- `generate_sample_data.py` - General-purpose sample data generation
  - Creates diverse test datasets
  - Supports multiple data formats
  - Configurable data volumes

## Usage

```bash
# Generate sample blind evaluation data
python samples/create_sample_blind_data.py

# Generate sample batch metrics
python samples/create_sample_batch_data.py

# Generate general sample data
python samples/generate_sample_data.py
```

## Purpose
- **Testing**: Provide realistic data for development testing
- **Demos**: Create compelling demonstrations of system capabilities
- **Development**: Support feature development without needing real user data
- **CI/CD**: Enable automated testing with consistent datasets

## Output
Generated sample data is typically saved to:
- Local JSON files for immediate testing
- GCS storage for cloud integration testing
- In-memory structures for unit tests 