"""
Security Configuration Module

This module provides centralized security settings and utilities for the LLM Evaluation System.
It helps prevent common security vulnerabilities and ensures secure defaults.
"""

import re
import os
import hashlib
from typing import Optional, List
import logging

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/security.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration and utilities."""
    
    # Email validation pattern (RFC 5322 compliant)
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Allowed file extensions for uploads
    ALLOWED_FILE_EXTENSIONS = {'.csv', '.json', '.txt'}
    
    # Maximum file size (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    # Session timeout (24 hours)
    SESSION_TIMEOUT_HOURS = 24
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format using robust regex.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        return bool(SecurityConfig.EMAIL_PATTERN.match(email.strip()))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unknown"
        
        # Remove any path components
        filename = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Ensure it doesn't start with a dot (hidden file)
        if filename.startswith('.'):
            filename = '_' + filename[1:]
        
        return filename[:100]  # Limit length
    
    @staticmethod
    def validate_file_path(file_path: str, allowed_dirs: List[str]) -> bool:
        """
        Validate that a file path is within allowed directories.
        
        Args:
            file_path: File path to validate
            allowed_dirs: List of allowed base directories
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            # Normalize the path
            normalized_path = os.path.normpath(file_path)
            
            # Check if path tries to escape allowed directories
            for allowed_dir in allowed_dirs:
                allowed_dir_norm = os.path.normpath(allowed_dir)
                if normalized_path.startswith(allowed_dir_norm):
                    return True
            
            return False
        except Exception:
            return False
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """
        Hash a password with salt using SHA-256.
        
        Args:
            password: Password to hash
            salt: Optional salt (will generate if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            import secrets
            salt = secrets.token_hex(32)
        
        # Hash password with salt
        salted_password = (password + salt).encode('utf-8')
        hashed = hashlib.sha256(salted_password).hexdigest()
        
        return hashed, salt
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Stored hash
            salt: Salt used for hashing
            
        Returns:
            True if password matches, False otherwise
        """
        computed_hash, _ = SecurityConfig.hash_password(password, salt)
        return computed_hash == hashed_password
    
    @staticmethod
    def sanitize_error_message(error_message: str) -> str:
        """
        Sanitize error messages to prevent information disclosure.
        
        Args:
            error_message: Original error message
            
        Returns:
            Sanitized error message
        """
        # Remove common sensitive information patterns
        sensitive_patterns = [
            r'password[s]?[\s]*[=:]\s*[^\s]+',
            r'key[s]?[\s]*[=:]\s*[^\s]+',
            r'token[s]?[\s]*[=:]\s*[^\s]+',
            r'secret[s]?[\s]*[=:]\s*[^\s]+',
            r'/[a-zA-Z0-9]+/[a-zA-Z0-9]+',  # File paths
            r'[a-zA-Z]:\\\w+',  # Windows paths
        ]
        
        sanitized = error_message
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        # Limit error message length
        return sanitized[:200] + "..." if len(sanitized) > 200 else sanitized
    
    @staticmethod
    def log_security_event(event_type: str, details: str, user_email: Optional[str] = None):
        """
        Log security-related events.
        
        Args:
            event_type: Type of security event
            details: Event details
            user_email: Optional user email
        """
        user_info = f" User: {user_email}" if user_email else ""
        logger.warning(f"SECURITY EVENT - {event_type}: {details}{user_info}")

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)