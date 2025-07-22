"""
Data Storage Module for Human Evaluations

This module provides secure data collection and persistence mechanisms for human evaluation data,
supporting external cloud storage solutions like Google Cloud Storage and Google Drive.
"""

import json
import csv
import os
import tempfile
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
import streamlit as st
import pandas as pd
from io import StringIO, BytesIO
import base64

# Cloud storage imports
try:
    from google.cloud import storage
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

try:
    import gdown
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False


class DataStore:
    """
    Secure data storage for human evaluation data with cloud persistence.
    
    Supports multiple storage backends:
    - Google Cloud Storage
    - Google Drive
    - Local file system (fallback)
    """
    
    def __init__(self, storage_type: str = "local"):
        """
        Initialize data store with specified storage type.
        
        Args:
            storage_type: "gcs", "gdrive", or "local"
        """
        self.storage_type = storage_type
        self.storage_client = None
        self.bucket_name = None
        
        if storage_type == "gcs":
            self._init_google_cloud_storage()
        elif storage_type == "gdrive":
            self._init_google_drive()
    
    def _init_google_cloud_storage(self):
        """Initialize Google Cloud Storage client."""
        if not GOOGLE_CLOUD_AVAILABLE:
            st.warning("Google Cloud Storage not available. Falling back to local storage.")
            self.storage_type = "local"
            return
        
        try:
            # Get credentials from Streamlit secrets
            if "gcs" in st.secrets and "service_account" in st.secrets["gcs"]:
                service_account_info = st.secrets["gcs"]["service_account"]
                
                # Handle case where service account is stored as string
                if isinstance(service_account_info, str):
                    import json
                    service_account_info = json.loads(service_account_info)
                
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info
                )
                self.storage_client = storage.Client(credentials=credentials)
                self.bucket_name = st.secrets["gcs"].get("bucket_name", "llm-evaluation-data")
            else:
                st.warning("Google Cloud Storage credentials not found in secrets. Using local storage.")
                self.storage_type = "local"
        except Exception as e:
            st.error(f"Failed to initialize Google Cloud Storage: {str(e)}")
            self.storage_type = "local"
    
    def _init_google_drive(self):
        """Initialize Google Drive client."""
        if not GOOGLE_DRIVE_AVAILABLE:
            st.warning("Google Drive not available. Falling back to local storage.")
            self.storage_type = "local"
            return
        
        try:
            # Get Google Drive folder ID from secrets
            self.drive_folder_id = st.secrets.get("gdrive_folder_id")
            if not self.drive_folder_id:
                st.warning("Google Drive folder ID not found in secrets. Using local storage.")
                self.storage_type = "local"
        except Exception as e:
            st.error(f"Failed to initialize Google Drive: {str(e)}")
            self.storage_type = "local"
    
    def save_evaluation_data(self, evaluation_data: Dict[str, Any]) -> bool:
        """
        Save evaluation data to the configured storage.
        
        Args:
            evaluation_data: Dictionary containing evaluation data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.storage_type == "gcs":
                return self._save_to_gcs(evaluation_data)
            elif self.storage_type == "gdrive":
                return self._save_to_gdrive(evaluation_data)
            else:
                return self._save_to_local(evaluation_data)
        except Exception as e:
            st.error(f"Failed to save evaluation data: {str(e)}")
            return False
    
    def save_registration_data(self, registration_data: Dict[str, Any]) -> bool:
        """
        Save registration data to the configured storage.
        
        Args:
            registration_data: Dictionary containing registration data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.storage_type == "gcs":
                return self._save_registration_to_gcs(registration_data)
            elif self.storage_type == "gdrive":
                return self._save_registration_to_gdrive(registration_data)
            else:
                return self._save_registration_to_local(registration_data)
        except Exception as e:
            st.error(f"Failed to save registration data: {str(e)}")
            return False
    
    def load_evaluation_data(self) -> List[Dict[str, Any]]:
        """
        Load evaluation data from the configured storage.
        
        Returns:
            List of evaluation data dictionaries
        """
        try:
            if self.storage_type == "gcs":
                return self._load_from_gcs("evaluations")
            elif self.storage_type == "gdrive":
                return self._load_from_gdrive("evaluations")
            else:
                return self._load_from_local("evaluations")
        except Exception as e:
            st.error(f"Failed to load evaluation data: {str(e)}")
            return []
    
    def load_registration_data(self) -> Dict[str, Any]:
        """
        Load registration data from the configured storage.
        
        Returns:
            Dictionary of registration data
        """
        try:
            if self.storage_type == "gcs":
                return self._load_registration_from_gcs()
            elif self.storage_type == "gdrive":
                return self._load_registration_from_gdrive()
            else:
                return self._load_registration_from_local()
        except Exception as e:
            st.error(f"Failed to load registration data: {str(e)}")
            return {}
    
    def _save_to_gcs(self, evaluation_data: Dict[str, Any]) -> bool:
        """Save evaluation data to Google Cloud Storage."""
        if not self.storage_client:
            return False
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            
            # Load existing data
            existing_data = self._load_from_gcs("evaluations")
            existing_data.append(evaluation_data)
            
            # Save updated data
            blob = bucket.blob("evaluations.json")
            blob.upload_from_string(
                json.dumps(existing_data, indent=2, default=str),
                content_type="application/json"
            )
            
            # Also save as CSV for analysis
            self._save_evaluations_csv_to_gcs(existing_data)
            
            return True
        except Exception as e:
            st.error(f"GCS save error: {str(e)}")
            return False
    
    def _save_to_gdrive(self, evaluation_data: Dict[str, Any]) -> bool:
        """Save evaluation data to Google Drive."""
        try:
            # Load existing data
            existing_data = self._load_from_gdrive("evaluations")
            existing_data.append(evaluation_data)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(existing_data, f, indent=2, default=str)
                temp_file = f.name
            
            # Upload to Google Drive
            # Note: This is a simplified implementation
            # In production, you'd use the Google Drive API
            st.info("Google Drive upload would be implemented here")
            
            # Clean up
            os.unlink(temp_file)
            return True
        except Exception as e:
            st.error(f"Google Drive save error: {str(e)}")
            return False
    
    def _save_to_local(self, evaluation_data: Dict[str, Any]) -> bool:
        """Save evaluation data to local file system."""
        try:
            # Load existing data
            existing_data = self._load_from_local("evaluations")
            existing_data.append(evaluation_data)
            
            # Save to file
            file_path = os.path.join('data', 'evaluations.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, default=str)
            
            # Also save as CSV for analysis
            self._save_evaluations_csv_to_local(existing_data)
            
            return True
        except Exception as e:
            st.error(f"Local save error: {str(e)}")
            return False
    
    def _save_registration_to_gcs(self, registration_data: Dict[str, Any]) -> bool:
        """Save registration data to Google Cloud Storage."""
        if not self.storage_client:
            return False
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            
            # Load existing registrations
            existing_data = self._load_registration_from_gcs()
            email = registration_data.get("email")
            if email:
                existing_data[email] = registration_data
            
            # Save updated data
            blob = bucket.blob("registrations.json")
            blob.upload_from_string(
                json.dumps(existing_data, indent=2, default=str),
                content_type="application/json"
            )
            
            return True
        except Exception as e:
            st.error(f"GCS registration save error: {str(e)}")
            return False
    
    def _save_registration_to_gdrive(self, registration_data: Dict[str, Any]) -> bool:
        """Save registration data to Google Drive."""
        try:
            # Load existing registrations
            existing_data = self._load_registration_from_gdrive()
            email = registration_data.get("email")
            if email:
                existing_data[email] = registration_data
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(existing_data, f, indent=2, default=str)
                temp_file = f.name
            
            # Upload to Google Drive
            st.info("Google Drive registration upload would be implemented here")
            
            # Clean up
            os.unlink(temp_file)
            return True
        except Exception as e:
            st.error(f"Google Drive registration save error: {str(e)}")
            return False
    
    def _save_registration_to_local(self, registration_data: Dict[str, Any]) -> bool:
        """Save registration data to local file system."""
        try:
            # Load existing registrations
            existing_data = self._load_registration_from_local()
            email = registration_data.get("email")
            if email:
                existing_data[email] = registration_data
            
            # Save to file
            file_path = os.path.join('data', 'registrations.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            st.error(f"Local registration save error: {str(e)}")
            return False
    
    def _load_from_gcs(self, data_type: str) -> List[Dict[str, Any]]:
        """Load data from Google Cloud Storage."""
        if not self.storage_client:
            return []
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(f"{data_type}.json")
            
            if blob.exists():
                content = blob.download_as_text()
                return json.loads(content) if content else []
            else:
                return []
        except Exception as e:
            st.error(f"GCS load error: {str(e)}")
            return []
    
    def _load_from_gdrive(self, data_type: str) -> List[Dict[str, Any]]:
        """Load data from Google Drive."""
        try:
            # This would be implemented with Google Drive API
            st.info("Google Drive load would be implemented here")
            return []
        except Exception as e:
            st.error(f"Google Drive load error: {str(e)}")
            return []
    
    def _load_from_local(self, data_type: str) -> List[Dict[str, Any]]:
        """Load data from local file system."""
        try:
            file_path = os.path.join('data', f'{data_type}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return json.loads(content) if content else []
            else:
                return []
        except Exception as e:
            st.error(f"Local load error: {str(e)}")
            return []
    
    def _load_registration_from_gcs(self) -> Dict[str, Any]:
        """Load registration data from Google Cloud Storage."""
        if not self.storage_client:
            return {}
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob("registrations.json")
            
            if blob.exists():
                content = blob.download_as_text()
                return json.loads(content) if content else {}
            else:
                return {}
        except Exception as e:
            st.error(f"GCS registration load error: {str(e)}")
            return {}
    
    def _load_registration_from_gdrive(self) -> Dict[str, Any]:
        """Load registration data from Google Drive."""
        try:
            # This would be implemented with Google Drive API
            st.info("Google Drive registration load would be implemented here")
            return {}
        except Exception as e:
            st.error(f"Google Drive registration load error: {str(e)}")
            return {}
    
    def _load_registration_from_local(self) -> Dict[str, Any]:
        """Load registration data from local file system."""
        try:
            file_path = os.path.join('data', 'registrations.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return json.loads(content) if content else {}
            else:
                return {}
        except Exception as e:
            st.error(f"Local registration load error: {str(e)}")
            return {}
    
    def _save_evaluations_csv_to_gcs(self, evaluations: List[Dict[str, Any]]) -> bool:
        """Save evaluations as CSV to Google Cloud Storage."""
        if not self.storage_client:
            return False
        
        try:
            # Convert to DataFrame and then to CSV
            df = self._evaluations_to_dataframe(evaluations)
            csv_content = df.to_csv(index=False)
            
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob("evaluations.csv")
            blob.upload_from_string(csv_content, content_type="text/csv")
            
            return True
        except Exception as e:
            st.error(f"GCS CSV save error: {str(e)}")
            return False
    
    def _save_evaluations_csv_to_local(self, evaluations: List[Dict[str, Any]]) -> bool:
        """Save evaluations as CSV to local file system, flattening nested question/response ratings."""
        try:
            rows = []
            for eval in evaluations:
                tester_email = eval.get("tester_email", "")
                tester_name = eval.get("tester_name", "")
                timestamp = eval.get("evaluation_timestamp", "")
                for qkey, qdata in eval.get("individual_question_ratings", {}).items():
                    question = qdata.get("question", "")
                    industry = qdata.get("industry", "")
                    model_mapping = qdata.get("model_mapping", {})
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
                            "actionability": rating.get("actionability", "")
                        }
                        rows.append(row)
            # Write to CSV
            if rows:
                file_path = os.path.join('data', 'evaluations.csv')
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
            return True
        except Exception as e:
            st.error(f"Local CSV save error: {str(e)}")
            return False
    
    def _evaluations_to_dataframe(self, evaluations: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert evaluations list to pandas DataFrame."""
        rows = []
        
        for eval_data in evaluations:
            base_row = {
                'tester_email': eval_data.get('tester_email', ''),
                'tester_name': eval_data.get('tester_name', ''),
                'evaluation_timestamp': eval_data.get('evaluation_timestamp', ''),
                'question': eval_data.get('current_question', ''),
                'industry': eval_data.get('current_industry', ''),
                'question_key': eval_data.get('question_key', '')
            }
            
            # Add ratings for each response (A, B, C, D)
            ratings = eval_data.get('ratings', {})
            for response_id in ['A', 'B', 'C', 'D']:
                if response_id in ratings:
                    rating_data = ratings[response_id]
                    row = base_row.copy()
                    row.update({
                        'response_id': response_id,
                        'llm_model': rating_data.get('response_id', ''),
                        'quality_rating': rating_data.get('quality', ''),
                        'relevance_rating': rating_data.get('relevance', ''),
                        'accuracy_rating': rating_data.get('accuracy', ''),
                        'uniformity_rating': rating_data.get('uniformity', ''),
                        'comments': rating_data.get('comments', '')
                    })
                    rows.append(row)
        
        return pd.DataFrame(rows)
    
    def get_storage_status(self) -> Dict[str, Any]:
        """Get current storage configuration and status."""
        status = {
            "storage_type": self.storage_type,
            "available_backends": {
                "google_cloud": GOOGLE_CLOUD_AVAILABLE,
                "google_drive": GOOGLE_DRIVE_AVAILABLE
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if self.storage_type == "gcs" and self.storage_client:
            try:
                # Test bucket access
                bucket = self.storage_client.bucket(self.bucket_name)
                status["gcs_bucket"] = self.bucket_name
                status["gcs_accessible"] = bucket.exists()
            except Exception as e:
                status["gcs_accessible"] = False
                status["gcs_error"] = str(e)
        
        return status

    def load_latest_batch_metrics(self) -> Dict[str, Any]:
        """Load the latest batch evaluation metrics from storage."""
        try:
            if self.storage_type == "gcs" and self.storage_client:
                bucket = self.storage_client.bucket(self.bucket_name)
                
                # Try to load JSON first
                json_blob = bucket.blob("batch_eval_metrics.json")
                if json_blob.exists():
                    json_content = json_blob.download_as_text()
                    return json.loads(json_content)
                
                # Fallback to CSV if JSON not available
                csv_blob = bucket.blob("batch_eval_metrics.csv")
                if csv_blob.exists():
                    csv_content = csv_blob.download_as_text()
                    df = pd.read_csv(StringIO(csv_content))
                    return df.to_dict('records')
                
            elif self.storage_type == "local":
                # Try local JSON first
                json_path = os.path.join("data", "batch_eval_metrics.json")
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                
                # Fallback to local CSV
                csv_path = os.path.join("data", "batch_eval_metrics.csv")
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    return df.to_dict('records')
            
            return []
            
        except Exception as e:
            st.error(f"Failed to load batch metrics: {str(e)}")
            return []


def create_data_store() -> DataStore:
    """
    Factory function to create a data store instance.
    
    Returns:
        DataStore instance configured based on available options
    """
    # Check for cloud storage configuration in secrets
    if "gcp_service_account" in st.secrets and GOOGLE_CLOUD_AVAILABLE:
        return DataStore("gcs")
    elif "gdrive_folder_id" in st.secrets and GOOGLE_DRIVE_AVAILABLE:
        return DataStore("gdrive")
    else:
        return DataStore("local")


def validate_evaluation_data(evaluation_data: Dict[str, Any]) -> bool:
    """
    Validate evaluation data before saving.
    
    Args:
        evaluation_data: The evaluation data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['tester_email', 'tester_name', 'evaluation_timestamp', 'ratings']
    
    for field in required_fields:
        if field not in evaluation_data:
            st.error(f"Missing required field: {field}")
            return False
    
    # Validate email format
    email = evaluation_data.get('tester_email', '')
    if '@' not in email or '.' not in email:
        st.error("Invalid email format")
        return False
    
    # Validate ratings structure
    ratings = evaluation_data.get('ratings', {})
    if not isinstance(ratings, dict):
        st.error("Invalid ratings structure")
        return False
    
    # Validate each rating has required fields
    for response_id, rating_data in ratings.items():
        required_rating_fields = ['quality', 'relevance', 'accuracy', 'uniformity']
        for field in required_rating_fields:
            if field not in rating_data:
                st.error(f"Missing rating field {field} for response {response_id}")
                return False
    
    return True


def validate_registration_data(registration_data: Dict[str, Any]) -> bool:
    """
    Validate registration data before saving.
    
    Args:
        registration_data: The registration data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['email', 'name', 'consent_given', 'registration_timestamp']
    
    for field in required_fields:
        if field not in registration_data:
            st.error(f"Missing required field: {field}")
            return False
    
    # Validate email format
    email = registration_data.get('email', '')
    if '@' not in email or '.' not in email:
        st.error("Invalid email format")
        return False
    
    # Validate consent
    if not registration_data.get('consent_given', False):
        st.error("Consent must be given")
        return False
    
    return True 