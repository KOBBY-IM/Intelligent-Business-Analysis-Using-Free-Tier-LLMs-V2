"""
Unit tests for the data store module.

Tests data serialization, validation, and storage functionality.
"""

import unittest
import json
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.data_store import (
    DataStore, 
    create_data_store, 
    validate_evaluation_data, 
    validate_registration_data
)


class TestDataStore(unittest.TestCase):
    """Test cases for the DataStore class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_store = DataStore("local")
        
        # Sample evaluation data
        self.sample_evaluation = {
            "tester_email": "test@example.com",
            "tester_name": "Test User",
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
        
        # Sample registration data
        self.sample_registration = {
            "name": "Test User",
            "email": "test@example.com",
            "consent_given": True,
            "consent_timestamp": datetime.utcnow().isoformat(),
            "registration_timestamp": datetime.utcnow().isoformat(),
            "evaluation_completed": False,
            "session_id": "tester"
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_data_store_initialization(self):
        """Test DataStore initialization."""
        # Test local storage
        local_store = DataStore("local")
        self.assertEqual(local_store.storage_type, "local")
        
        # Test with invalid storage type
        invalid_store = DataStore("invalid")
        self.assertEqual(invalid_store.storage_type, "invalid")
    
    @patch('utils.data_store.GOOGLE_CLOUD_AVAILABLE', True)
    @patch('utils.data_store.st.secrets', {})
    def test_gcs_initialization_without_credentials(self):
        """Test GCS initialization without credentials."""
        store = DataStore("gcs")
        self.assertEqual(store.storage_type, "local")  # Should fallback to local
    
    @patch('utils.data_store.GOOGLE_DRIVE_AVAILABLE', True)
    @patch('utils.data_store.st.secrets', {})
    def test_gdrive_initialization_without_folder_id(self):
        """Test Google Drive initialization without folder ID."""
        store = DataStore("gdrive")
        self.assertEqual(store.storage_type, "local")  # Should fallback to local
    
    def test_validate_evaluation_data_valid(self):
        """Test validation of valid evaluation data."""
        self.assertTrue(validate_evaluation_data(self.sample_evaluation))
    
    def test_validate_evaluation_data_missing_fields(self):
        """Test validation of evaluation data with missing fields."""
        invalid_data = self.sample_evaluation.copy()
        del invalid_data["tester_email"]
        
        self.assertFalse(validate_evaluation_data(invalid_data))
    
    def test_validate_evaluation_data_invalid_email(self):
        """Test validation of evaluation data with invalid email."""
        invalid_data = self.sample_evaluation.copy()
        invalid_data["tester_email"] = "invalid-email"
        
        self.assertFalse(validate_evaluation_data(invalid_data))
    
    def test_validate_evaluation_data_invalid_ratings(self):
        """Test validation of evaluation data with invalid ratings."""
        invalid_data = self.sample_evaluation.copy()
        invalid_data["ratings"] = "not_a_dict"
        
        self.assertFalse(validate_evaluation_data(invalid_data))
    
    def test_validate_evaluation_data_missing_rating_fields(self):
        """Test validation of evaluation data with missing rating fields."""
        invalid_data = self.sample_evaluation.copy()
        invalid_data["ratings"]["A"] = {"quality": 4}  # Missing other fields
        
        self.assertFalse(validate_evaluation_data(invalid_data))
    
    def test_validate_registration_data_valid(self):
        """Test validation of valid registration data."""
        self.assertTrue(validate_registration_data(self.sample_registration))
    
    def test_validate_registration_data_missing_fields(self):
        """Test validation of registration data with missing fields."""
        invalid_data = self.sample_registration.copy()
        del invalid_data["email"]
        
        self.assertFalse(validate_registration_data(invalid_data))
    
    def test_validate_registration_data_invalid_email(self):
        """Test validation of registration data with invalid email."""
        invalid_data = self.sample_registration.copy()
        invalid_data["email"] = "invalid-email"
        
        self.assertFalse(validate_registration_data(invalid_data))
    
    def test_validate_registration_data_no_consent(self):
        """Test validation of registration data without consent."""
        invalid_data = self.sample_registration.copy()
        invalid_data["consent_given"] = False
        
        self.assertFalse(validate_registration_data(invalid_data))
    
    def test_evaluations_to_dataframe(self):
        """Test conversion of evaluations to DataFrame."""
        evaluations = [self.sample_evaluation]
        df = _evaluations_to_dataframe(evaluations)
        
        # Check that DataFrame has expected columns
        expected_columns = [
            'tester_email', 'tester_name', 'evaluation_timestamp', 
            'question', 'industry', 'question_key', 'response_id', 
            'llm_model', 'quality_rating', 'relevance_rating', 
            'accuracy_rating', 'uniformity_rating', 'comments'
        ]
        
        for col in expected_columns:
            self.assertIn(col, df.columns)
        
        # Check that we have rows for each response (A and B in this case)
        self.assertEqual(len(df), 2)
        
        # Check that data is correctly populated
        self.assertEqual(df.iloc[0]['tester_email'], 'test@example.com')
        self.assertEqual(df.iloc[0]['quality_rating'], 4)
        self.assertEqual(df.iloc[1]['quality_rating'], 3)
    
    def test_evaluations_to_dataframe_empty(self):
        """Test conversion of empty evaluations list."""
        df = _evaluations_to_dataframe([])
        self.assertEqual(len(df), 0)
    
    def test_get_storage_status(self):
        """Test storage status information."""
        status = self.data_store.get_storage_status()
        
        expected_keys = [
            'storage_type', 'gcs_available', 'gdrive_available', 
            'gcs_configured', 'gdrive_configured'
        ]
        
        for key in expected_keys:
            self.assertIn(key, status)
        
        self.assertEqual(status['storage_type'], 'local')
    
    @patch('utils.data_store.GOOGLE_CLOUD_AVAILABLE', True)
    @patch('utils.data_store.GOOGLE_DRIVE_AVAILABLE', True)
    def test_create_data_store_fallback(self):
        """Test data store creation with fallback to local."""
        # Test without any cloud credentials
        with patch('utils.data_store.st.secrets', {}):
            store = create_data_store()
            self.assertEqual(store.storage_type, 'local')
    
    def test_save_and_load_local(self):
        """Test saving and loading data locally."""
        # Test evaluation data
        success = self.data_store.save_evaluation_data(self.sample_evaluation)
        self.assertTrue(success)
        
        loaded_data = self.data_store.load_evaluation_data()
        self.assertEqual(len(loaded_data), 1)
        self.assertEqual(loaded_data[0]['tester_email'], 'test@example.com')
        
        # Test registration data
        success = self.data_store.save_registration_data(self.sample_registration)
        self.assertTrue(success)
        
        loaded_registrations = self.data_store.load_registration_data()
        self.assertIn('test@example.com', loaded_registrations)
        self.assertEqual(loaded_registrations['test@example.com']['name'], 'Test User')
    
    def test_data_persistence_across_instances(self):
        """Test that data persists across different DataStore instances."""
        # Save data with first instance
        store1 = DataStore("local")
        store1.save_evaluation_data(self.sample_evaluation)
        
        # Load data with second instance
        store2 = DataStore("local")
        loaded_data = store2.load_evaluation_data()
        
        self.assertEqual(len(loaded_data), 1)
        self.assertEqual(loaded_data[0]['tester_email'], 'test@example.com')
    
    def test_handle_special_characters(self):
        """Test handling of special characters in data."""
        # Test with special characters in comments
        special_evaluation = self.sample_evaluation.copy()
        special_evaluation['ratings']['A']['comments'] = "Special chars: éñç@#$%^&*()"
        
        success = self.data_store.save_evaluation_data(special_evaluation)
        self.assertTrue(success)
        
        loaded_data = self.data_store.load_evaluation_data()
        self.assertEqual(
            loaded_data[0]['ratings']['A']['comments'], 
            "Special chars: éñç@#$%^&*()"
        )
    
    def test_handle_long_data(self):
        """Test handling of very long data fields."""
        # Test with very long comments
        long_evaluation = self.sample_evaluation.copy()
        long_evaluation['ratings']['A']['comments'] = "A" * 10000  # 10k character comment
        
        success = self.data_store.save_evaluation_data(long_evaluation)
        self.assertTrue(success)
        
        loaded_data = self.data_store.load_evaluation_data()
        self.assertEqual(len(loaded_data[0]['ratings']['A']['comments']), 10000)
    
    def test_handle_empty_fields(self):
        """Test handling of empty fields."""
        # Test with empty comments
        empty_evaluation = self.sample_evaluation.copy()
        empty_evaluation['ratings']['A']['comments'] = ""
        
        success = self.data_store.save_evaluation_data(empty_evaluation)
        self.assertTrue(success)
        
        loaded_data = self.data_store.load_evaluation_data()
        self.assertEqual(loaded_data[0]['ratings']['A']['comments'], "")
    
    def test_incremental_data_append(self):
        """Test that data is appended incrementally, not overwritten."""
        # Save first evaluation
        evaluation1 = self.sample_evaluation.copy()
        evaluation1['tester_email'] = 'user1@example.com'
        self.data_store.save_evaluation_data(evaluation1)
        
        # Save second evaluation
        evaluation2 = self.sample_evaluation.copy()
        evaluation2['tester_email'] = 'user2@example.com'
        self.data_store.save_evaluation_data(evaluation2)
        
        # Load all data
        loaded_data = self.data_store.load_evaluation_data()
        
        # Should have both evaluations
        self.assertEqual(len(loaded_data), 2)
        emails = [e['tester_email'] for e in loaded_data]
        self.assertIn('user1@example.com', emails)
        self.assertIn('user2@example.com', emails)


class TestDataStoreIntegration(unittest.TestCase):
    """Integration tests for data store functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_store = DataStore("local")
    
    def test_full_evaluation_workflow(self):
        """Test complete evaluation workflow with data persistence."""
        # Simulate registration
        registration = {
            "name": "Integration Test User",
            "email": "integration@example.com",
            "consent_given": True,
            "consent_timestamp": datetime.utcnow().isoformat(),
            "registration_timestamp": datetime.utcnow().isoformat(),
            "evaluation_completed": False,
            "session_id": "tester"
        }
        
        # Save registration
        success = self.data_store.save_registration_data(registration)
        self.assertTrue(success)
        
        # Simulate multiple evaluations
        for i in range(3):
            evaluation = {
                "tester_email": "integration@example.com",
                "tester_name": "Integration Test User",
                "evaluation_timestamp": datetime.utcnow().isoformat(),
                "current_question": f"Test question {i+1}",
                "current_industry": "retail",
                "question_key": f"retail:test_question_{i+1}",
                "ratings": {
                    "A": {
                        "quality": 4,
                        "relevance": 5,
                        "accuracy": 4,
                        "uniformity": 3,
                        "comments": f"Test comment {i+1}",
                        "response_id": f"model_{i+1}"
                    }
                }
            }
            
            success = self.data_store.save_evaluation_data(evaluation)
            self.assertTrue(success)
        
        # Verify all data is persisted
        registrations = self.data_store.load_registration_data()
        evaluations = self.data_store.load_evaluation_data()
        
        self.assertIn('integration@example.com', registrations)
        self.assertEqual(len(evaluations), 3)
        
        # Verify all evaluations belong to the same user
        for evaluation in evaluations:
            self.assertEqual(evaluation['tester_email'], 'integration@example.com')


if __name__ == '__main__':
    unittest.main() 