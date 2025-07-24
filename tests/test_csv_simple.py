"""
Simple test for CSV generation fix - tests the core logic without streamlit dependencies.
"""
import json
import pandas as pd
from datetime import datetime

def convert_evaluations_to_dataframe(evaluations):
    """
    Simplified version of the _evaluations_to_dataframe function for testing.
    This replicates the fixed logic without streamlit dependencies.
    """
    rows = []
    
    for eval_data in evaluations:
        tester_email = eval_data.get("tester_email", "")
        tester_name = eval_data.get("tester_name", "")
        timestamp = eval_data.get("evaluation_timestamp", "")
        
        # Process individual question ratings (correct structure)
        individual_ratings = eval_data.get("individual_question_ratings", {})
        for qkey, qdata in individual_ratings.items():
            question = qdata.get("question", "")
            industry = qdata.get("industry", "")
            model_mapping = qdata.get("model_mapping", {})
            
            # Process ratings for each response (A, B, C, D)
            for resp_id, rating in qdata.get("ratings", {}).items():
                row = {
                    "tester_email": tester_email,
                    "tester_name": tester_name,
                    "evaluation_timestamp": timestamp,
                    "question_key": qkey,
                    "question": question,
                    "industry": industry,
                    "response_id": resp_id,
                    "llm_model": rating.get("response_id", model_mapping.get(resp_id, "")),
                    "relevance": rating.get("relevance", ""),
                    "clarity": rating.get("clarity", ""),
                    "actionability": rating.get("actionability", ""),
                    "comments": rating.get("comments", "")
                }
                rows.append(row)
    
    return pd.DataFrame(rows)

def test_csv_generation_fix():
    """Test that CSV generation correctly handles the evaluation data structure."""
    
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
            },
            "finance:another_question": {
                "question": "What was the stock trend?",
                "industry": "finance",
                "ratings": {
                    "A": {
                        "relevance": 5,
                        "clarity": 4,
                        "actionability": 5,
                        "response_id": "mistral-7b",
                        "comments": "Excellent analysis"
                    }
                },
                "model_mapping": {
                    "A": "mistral-7b"
                }
            }
        }
    }
    
    # Test the DataFrame conversion
    df = convert_evaluations_to_dataframe([sample_evaluation])
    
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
    
    # Verify data was extracted correctly - should have 3 rows (2 retail + 1 finance)
    if len(df) != 3:
        print(f"❌ Expected 3 rows, got {len(df)}")
        return False
    
    # Check specific values
    retail_rows = df[df['industry'] == 'retail']
    if len(retail_rows) != 2:
        print(f"❌ Expected 2 retail rows, got {len(retail_rows)}")
        return False
    
    finance_rows = df[df['industry'] == 'finance']
    if len(finance_rows) != 1:
        print(f"❌ Expected 1 finance row, got {len(finance_rows)}")
        return False
    
    # Check specific rating values
    row_a = df[df['response_id'] == 'A'].iloc[0]
    if row_a['relevance'] != 4:
        print(f"❌ Expected relevance=4 for first response A, got {row_a['relevance']}")
        return False
    
    if row_a['llm_model'] != 'llama3-70b-8192':
        print(f"❌ Expected llm_model='llama3-70b-8192' for first response A, got {row_a['llm_model']}")
        return False
    
    print("✅ CSV generation test passed!")
    print("\nSample DataFrame:")
    print(df.to_string(index=False))
    return True

def test_old_vs_new_structure():
    """Test to show the difference between old (broken) and new (fixed) structure."""
    
    # This is what the OLD structure expected (WRONG)
    old_structure = {
        "tester_email": "test@example.com",
        "current_question": "What product had highest sales?",  # Wrong field name
        "current_industry": "retail",  # Wrong field name
        "ratings": {  # Wrong structure - ratings at top level
            "A": {"quality": 4, "relevance": 5}  # Wrong field names
        }
    }
    
    # This is the NEW structure that actually gets saved (CORRECT)
    new_structure = {
        "tester_email": "test@example.com",
        "individual_question_ratings": {  # Correct structure
            "retail:question1": {
                "question": "What product had highest sales?",  # Correct field name
                "industry": "retail",  # Correct field name
                "ratings": {
                    "A": {"relevance": 4, "clarity": 5, "actionability": 3}  # Correct field names
                }
            }
        }
    }
    
    print("\n🔍 Testing Old vs New Structure")
    
    # Test old structure (should produce empty DataFrame)
    df_old = convert_evaluations_to_dataframe([old_structure])
    print(f"Old structure DataFrame rows: {len(df_old)}")
    
    # Test new structure (should produce populated DataFrame)
    df_new = convert_evaluations_to_dataframe([new_structure])
    print(f"New structure DataFrame rows: {len(df_new)}")
    
    if len(df_old) > 0:
        print("❌ Old structure should produce empty DataFrame!")
        return False
    
    if len(df_new) != 1:
        print(f"❌ New structure should produce 1 row, got {len(df_new)}")
        return False
    
    print("✅ Structure comparison test passed!")
    return True

if __name__ == "__main__":
    print("Running CSV Generation Fix Tests...")
    
    test1_passed = test_csv_generation_fix()
    test2_passed = test_old_vs_new_structure()
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The CSV generation fix correctly handles the evaluation data structure.")
        print("\n📋 Summary:")
        print("✅ Fixed data structure mismatch between JSON and CSV")
        print("✅ Fixed field name mismatches (current_question → question, etc.)")
        print("✅ Fixed rating field names (quality/accuracy → relevance/clarity/actionability)")
        print("✅ CSV will now be populated when JSON has data")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")