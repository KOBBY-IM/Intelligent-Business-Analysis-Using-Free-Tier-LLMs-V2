# Tests

This directory contains test files for the LLM evaluation system.

## Directory Structure

### **Unit Tests** (`unit/`)

- **`test_error_tracking.py`** - Tests for enhanced error tracking functionality
  - Tests error type classification
  - Validates error handling in batch evaluator
  - Tests LLM client error handling
  - Verifies error data collection

### **Integration Tests** (`integration/`)

Integration tests for system components (to be added as needed).

## Running Tests

### **Unit Tests**

```bash
# Run specific unit test
python3 tests/unit/test_error_tracking.py

# Run all unit tests
python3 -m pytest tests/unit/
```

### **Integration Tests**

```bash
# Run integration tests
python3 -m pytest tests/integration/
```

## Test Categories

### **Error Tracking Tests**
- Validates error classification system
- Tests retry mechanisms
- Verifies error data persistence
- Tests error analysis functionality

### **Data Collection Tests**
- Tests evaluation data collection
- Validates data storage mechanisms
- Tests data retrieval and analysis

### **System Integration Tests**
- Tests component interactions
- Validates end-to-end workflows
- Tests error handling across components

## Test Dependencies

- pytest
- pandas
- json
- unittest.mock (for mocking)

## Test Data

Tests use sample data and mock responses to avoid affecting production data. 