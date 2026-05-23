"""
Password hashing and validation.
"""

from passlib.context import CryptContext
import re
import logging

logger = logging.getLogger(__name__)


class PasswordHandler:
    """Handler for password hashing and validation."""
    
    def __init__(self, rounds: int = 12):
        """
        Initialize password handler.
        
        Args:
            rounds: Number of rounds for bcrypt hashing
        """
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.rounds = rounds
        
        # Password requirements
        self.min_length = 12
        self.requires_uppercase = True
        self.requires_lowercase = True
        self.requires_digit = True
        self.requires_special = True
        self.special_chars = "!@#$%^&*"
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        return self.pwd_context.hash(password, rounds=self.rounds)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to verify against
            
        Returns:
            bool: True if password matches
        """
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
    
    def validate_password_complexity(self, password: str) -> tuple[bool, str]:
        """
        Validate password meets complexity requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters long"
        
        if self.requires_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if self.requires_lowercase and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if self.requires_digit and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if self.requires_special and not any(c in self.special_chars for c in password):
            return False, f"Password must contain at least one special character: {self.special_chars}"
        
        return True, ""
    
    def validate_password(self, password: str, username: Optional[str] = None) -> tuple[bool, str]:
        """
        Validate password completely (complexity + username check).
        
        Args:
            password: Password to validate
            username: Username to check password doesn't contain
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check complexity
        is_valid, error_msg = self.validate_password_complexity(password)
        if not is_valid:
            return is_valid, error_msg
        
        # Check if password contains username
        if username and username.lower() in password.lower():
            return False, "Password cannot contain username"
        
        return True, ""
    
    def generate_password_reset_token(self) -> str:
        """
        Generate a secure password reset token.
        
        Returns:
            str: Random token
        """
        import secrets
        return secrets.token_urlsafe(32)
    
    def check_password_reuse(
        self,
        new_password: str,
        old_hashes: list[str],
        check_count: int = 5
    ) -> bool:
        """
        Check if new password is different from old passwords.
        
        Args:
            new_password: New password to check
            old_hashes: List of old password hashes
            check_count: Number of old passwords to check (default 5)
            
        Returns:
            bool: True if password is new (not reused)
        """
        # Only check the last check_count hashes
        hashes_to_check = old_hashes[-check_count:] if len(old_hashes) >= check_count else old_hashes
        
        for old_hash in hashes_to_check:
            if self.verify_password(new_password, old_hash):
                return False  # Password is reused
        
        return True  # Password is new


# Global password handler instance
from typing import Optional
password_handler = PasswordHandler()
