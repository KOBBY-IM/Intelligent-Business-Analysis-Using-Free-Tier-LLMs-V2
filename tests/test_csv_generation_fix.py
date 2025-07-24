"""
Test for CSV generation fix - verifies that evaluation data is correctly converted to CSV format.
"""
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.data_store import DataStore
import pandas as pd

def test_csv_generation_fix():
    """Test that CSV generation correctly handles the new evaluation data structure."""
    
    # Create sample evaluation data with the correct structure
    sample_evaluation = {
        "evaluation_id": "test-123-456",
        "tester_email": "test@example.com",
        "tester_name": "Test User",
        "evaluation_timestamp": datetime.now().isoformat(),
        "evaluation_type": "complete_evaluation",
        "individual_question_ratings": {
            "retail:test_question": {
                "question": "What product had the highest sales?",
                "industry": "retail",
                "ratings": {
                    "A": {
                        "relevance": 4,
                        "clarity": 5,
                        "actionability": 3,
                        "response_id": "llama3-70b-8192",
                        "comments": "Good analysis"
                    },
                    "B": {
                        "relevance": 3,
                        "clarity": 4,
                        "actionability": 4,
                        "response_id": "gemini-1.5-flash",
                        "comments": "Average response"
                    }
                },
                "model_mapping": {
                    "A": "llama3-70b-8192",
                    "B": "gemini-1.5-flash"
                }
            }
        }
    }
    
    # Test the DataFrame conversion
    data_store = DataStore("local")
    df = data_store._evaluations_to_dataframe([sample_evaluation])
    
    print("📊 Testing CSV Generation Fix")
    print(f"Generated DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Verify the DataFrame has the expected structure
    expected_columns = [
        "tester_email", "tester_name", "evaluation_timestamp", 
        "question_key", "question", "industry", "response_id", 
        "llm_model", "relevance", "clarity", "actionability", "comments"
    ]
    
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
        return False
    
    # Verify data was extracted correctly
    if len(df) != 2:  # Should have 2 rows (A and B responses)
        print(f"❌ Expected 2 rows, got {len(df)}")
        return False
    
    # Check specific values
    row_a = df[df['response_id'] == 'A'].iloc[0]
    if row_a['relevance'] != 4:
        print(f"❌ Expected relevance=4 for response A, got {row_a['relevance']}")
        return False
    
    if row_a['llm_model'] != 'llama3-70b-8192':
        print(f"❌ Expected llm_model='llama3-70b-8192' for response A, got {row_a['llm_model']}")
        return False
    
    print("✅ CSV generation test passed!")
    print("\nSample DataFrame:")
    print(df.to_string(index=False))
    return True

def test_empty_data_handling():
    """Test that empty evaluation data is handled correctly."""
    
    data_store = DataStore("local")
    
    # Test with empty list
    df_empty = data_store._evaluations_to_dataframe([])
    if len(df_empty) != 0:
        print(f"❌ Expected empty DataFrame, got {len(df_empty)} rows")
        return False
    
    # Test with evaluation having no individual_question_ratings
    eval_no_ratings = {
        "evaluation_id": "test-empty",
        "tester_email": "test@example.com",
        "tester_name": "Test User",
        "evaluation_timestamp": datetime.now().isoformat()
        # Missing individual_question_ratings
    }
    
    df_no_ratings = data_store._evaluations_to_dataframe([eval_no_ratings])
    if len(df_no_ratings) != 0:
        print(f"❌ Expected empty DataFrame for eval with no ratings, got {len(df_no_ratings)} rows")
        return False
    
    print("✅ Empty data handling test passed!")
    return True

if __name__ == "__main__":
    print("Running CSV Generation Fix Tests...")
    
    test1_passed = test_csv_generation_fix()
    test2_passed = test_empty_data_handling()
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! CSV generation fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")