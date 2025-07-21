# Tests Directory

This folder contains all test files for the Intelligent Business Analysis LLM project.

## Test Categories

### Unit Tests
- `test_data_store.py` - Tests for data storage and retrieval functionality
- `test_blind_evaluation.py` - Tests for blind evaluation system
- `test_rag_pipeline.py` - Tests for RAG pipeline components
- `test_registration.py` - Tests for user registration system

### Integration Tests
- `test_data_collection_gcs.py` - GCS data collection integration tests
- `test_gcs_*.py` - Various GCS connectivity and functionality tests
- `test_llm_connectivity.py` - LLM API connectivity tests
- `test_single_rag_llm.py` - Single LLM RAG functionality tests

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_data_store.py

# Run with verbose output
pytest -v
```

## Test Data
Tests use sample data and mock objects to avoid dependencies on external services during testing. 