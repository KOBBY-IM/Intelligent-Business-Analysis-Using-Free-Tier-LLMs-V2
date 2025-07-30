# Analysis Scripts

This directory contains analysis and testing scripts for the LLM evaluation system.

## Scripts Overview

### **Core Analysis Scripts**

- **`analyze_data.py`** - Comprehensive analysis of batch evaluation metrics data
  - Provider and model performance comparison
  - Industry-specific analysis
  - Error analysis and failure rates
  - Statistical insights and recommendations

### **Question Analysis Scripts**

- **`test_4_question_implementation.py`** - Verification script for 4-question implementation
  - Tests question selection logic
  - Validates statistical power
  - Analyzes question diversity
  - Simulates multiple testers

- **`question_reduction_impact_analysis.py`** - Analysis of reducing questions from 6 to 4 per industry
  - Impact on existing data
  - Statistical implications
  - User experience analysis
  - Recommendations

- **`question_reduction_analysis.py`** - General question reduction analysis
  - Statistical impact assessment
  - Data compatibility analysis
  - Implementation considerations

- **`random_selection_analysis.py`** - Analysis of random question selection strategy
  - Selection frequency analysis
  - Coverage assessment
  - Benefits and considerations

## Usage

Run any script from the project root:

```bash
python3 analysis_scripts/script_name.py
```

## Output

All scripts provide detailed console output with:
- Statistical analysis results
- Recommendations
- Implementation guidance
- Validation results

## Dependencies

- pandas
- numpy
- json
- random
- collections 