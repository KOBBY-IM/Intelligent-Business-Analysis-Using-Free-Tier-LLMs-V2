"""
Test Data Collection with Google Cloud Storage

This script tests the complete data collection system using GCS.
"""

import json
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from utils.data_store import DataStore, validate_evaluation_data, validate_registration_data

def test_data_collection_gcs():
    """Test the complete data collection system with GCS."""
    
    print("🧪 Testing Data Collection with Google Cloud Storage...")
    print("=" * 60)
    
    try:
        # Create data store with GCS
        print("1. Creating GCS data store...")
        data_store = DataStore("gcs")
        
        if data_store.storage_type != "gcs":
            print("❌ Failed to initialize GCS data store")
            return False
        
        print("✅ GCS data store created successfully")
        
        # Test registration data
        print("\n2. Testing registration data storage...")
        sample_registration = {
            "name": "Test User GCS",
            "email": "test-gcs@example.com",
            "consent_given": True,
            "consent_timestamp": datetime.utcnow().isoformat(),
            "registration_timestamp": datetime.utcnow().isoformat(),
            "evaluation_completed": False,
            "session_id": "tester"
        }
        
        # Validate registration data
        if not validate_registration_data(sample_registration):
            print("❌ Registration data validation failed")
            return False
        
        print("✅ Registration data validation passed")
        
        # Save registration data
        success = data_store.save_registration_data(sample_registration)
        if success:
            print("✅ Registration data saved to GCS")
        else:
            print("❌ Failed to save registration data")
            return False
        
        # Test evaluation data
        print("\n3. Testing evaluation data storage...")
        sample_evaluation = {
            "tester_email": "test-gcs@example.com",
            "tester_name": "Test User GCS",
            "evaluation_timestamp": datetime.utcnow().isoformat(),
            "current_question": "What product had the highest sales last quarter?",
            "current_industry": "retail",
            "question_key": "retail:test_question",
            "ratings": {
                "A": {
                    "quality": 4,
                    "relevance": 5,
                    "accuracy": 4,
                    "uniformity": 3,
                    "comments": "Excellent response with clear insights",
                    "response_id": "llama3-8b-8192"
                },
                "B": {
                    "quality": 3,
                    "relevance": 4,
                    "accuracy": 3,
                    "uniformity": 4,
                    "comments": "Good response but could be more detailed",
                    "response_id": "gemini-1.5-flash"
                }
            }
        }
        
        # Validate evaluation data
        if not validate_evaluation_data(sample_evaluation):
            print("❌ Evaluation data validation failed")
            return False
        
        print("✅ Evaluation data validation passed")
        
        # Save evaluation data
        success = data_store.save_evaluation_data(sample_evaluation)
        if success:
            print("✅ Evaluation data saved to GCS")
        else:
            print("❌ Failed to save evaluation data")
            return False
        
        # Load and verify data
        print("\n4. Testing data retrieval...")
        
        # Load registration data
        loaded_registrations = data_store.load_registration_data()
        if loaded_registrations and "test-gcs@example.com" in loaded_registrations:
            print("✅ Registration data retrieved from GCS")
        else:
            print("❌ Failed to retrieve registration data")
            return False
        
        # Load evaluation data
        loaded_evaluations = data_store.load_evaluation_data()
        if loaded_evaluations:
            # Find our test evaluation
            test_eval = None
            for eval_data in loaded_evaluations:
                if eval_data.get("tester_email") == "test-gcs@example.com":
                    test_eval = eval_data
                    break
            
            if test_eval:
                print("✅ Evaluation data retrieved from GCS")
                print(f"   Found evaluation with {len(test_eval['ratings'])} responses")
            else:
                print("❌ Test evaluation not found in loaded data")
                return False
        else:
            print("❌ Failed to retrieve evaluation data")
            return False
        
        # Test storage status
        print("\n5. Testing storage status...")
        status = data_store.get_storage_status()
        print(f"   Storage type: {status['storage_type']}")
        print(f"   GCS available: {status['gcs_available']}")
        print(f"   GCS configured: {status['gcs_configured']}")
        
        print("\n🎉 All GCS data collection tests passed!")
        print("   Your data collection system is ready for production use.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_data_collection_gcs()
    if not success:
        print("\n❌ Some tests failed. Please check the error messages above.") 