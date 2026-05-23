"""
Input validation utilities.
"""

import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class AccountValidator:
    """Validator for account-related inputs."""
    
    @staticmethod
    def validate_account_number(account_number: str) -> Tuple[bool, str]:
        """
        Validate account number format.
        
        Args:
            account_number: Account number to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not account_number:
            return False, "Account number is required"
        
        if len(account_number) < 5 or len(account_number) > 50:
            return False, "Account number must be between 5 and 50 characters"
        
        # Allow alphanumeric and hyphens/underscores
        if not re.match(r"^[a-zA-Z0-9\-_]+$", account_number):
            return False, "Account number must contain only alphanumeric characters, hyphens, and underscores"
        
        return True, ""
    
    @staticmethod
    def validate_mmi_id(mmi_id: str) -> Tuple[bool, str]:
        """
        Validate MMI ID format.
        
        Args:
            mmi_id: MMI ID to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not mmi_id:
            return False, "MMI ID is required"
        
        if len(mmi_id) > 50:
            return False, "MMI ID must not exceed 50 characters"
        
        return True, ""
    
    @staticmethod
    def validate_customer_name(name: str) -> Tuple[bool, str]:
        """
        Validate customer name.
        
        Args:
            name: Customer name to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not name:
            return False, "Customer name is required"
        
        if len(name) > 255:
            return False, "Customer name must not exceed 255 characters"
        
        # Allow letters, numbers, spaces, and common punctuation
        if not re.match(r"^[a-zA-Z0-9\s\-\.\,\&']+$", name):
            return False, "Customer name contains invalid characters"
        
        return True, ""


class TransactionValidator:
    """Validator for transaction-related inputs."""
    
    @staticmethod
    def validate_amount(amount: float, min_amount: float = 0.01, max_amount: float = 1000000.00) -> Tuple[bool, str]:
        """
        Validate transaction amount.
        
        Args:
            amount: Amount to validate
            min_amount: Minimum allowed amount
            max_amount: Maximum allowed amount
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if amount is None:
            return False, "Amount is required"
        
        if not isinstance(amount, (int, float)):
            return False, "Amount must be a number"
        
        if amount < min_amount:
            return False, f"Amount must be at least {min_amount}"
        
        if amount > max_amount:
            return False, f"Amount must not exceed {max_amount}"
        
        # Check for valid decimal precision (2 decimal places)
        if round(amount, 2) != amount:
            return False, "Amount must have at most 2 decimal places"
        
        return True, ""
    
    @staticmethod
    def validate_transaction_type(transaction_type: str, valid_types: list) -> Tuple[bool, str]:
        """
        Validate transaction type.
        
        Args:
            transaction_type: Type to validate
            valid_types: List of valid types
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not transaction_type:
            return False, "Transaction type is required"
        
        if transaction_type not in valid_types:
            return False, f"Invalid transaction type. Must be one of: {', '.join(valid_types)}"
        
        return True, ""
    
    @staticmethod
    def validate_reference_number(reference: str, max_length: int = 100) -> Tuple[bool, str]:
        """
        Validate reference number.
        
        Args:
            reference: Reference number to validate
            max_length: Maximum length allowed
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if reference and len(reference) > max_length:
            return False, f"Reference number must not exceed {max_length} characters"
        
        # Allow alphanumeric and common separators
        if reference and not re.match(r"^[a-zA-Z0-9\-\._/]+$", reference):
            return False, "Reference number contains invalid characters"
        
        return True, ""


class DateValidator:
    """Validator for date-related inputs."""
    
    @staticmethod
    def validate_date_range(start_date, end_date) -> Tuple[bool, str]:
        """
        Validate date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not start_date or not end_date:
            return False, "Both start and end dates are required"
        
        if start_date > end_date:
            return False, "Start date must be before end date"
        
        return True, ""


class InputValidator:
    """General input validation utilities."""
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Limit length if specified
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        if len(email) > 255:
            return False, "Email must not exceed 255 characters"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str, min_length: int = 3, max_length: int = 100) -> Tuple[bool, str]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
            min_length: Minimum length
            max_length: Maximum length
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"
        
        if len(username) < min_length:
            return False, f"Username must be at least {min_length} characters"
        
        if len(username) > max_length:
            return False, f"Username must not exceed {max_length} characters"
        
        # Allow letters, numbers, underscores, hyphens
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            return False, "Username must contain only letters, numbers, underscores, and hyphens"
        
        return True, ""
    
    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number (E.164 format).
        
        Args:
            phone: Phone number to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not phone:
            return False, "Phone number is required"
        
        # E.164 format: +1234567890
        if not re.match(r"^\+[1-9]\d{1,14}$", phone):
            return False, "Phone number must be in E.164 format (e.g., +12025551234)"
        
        return True, ""
    
    @staticmethod
    def is_safe_string(value: str) -> bool:
        """
        Check if string is safe from injection attacks.
        
        Args:
            value: String to check
            
        Returns:
            bool: True if safe
        """
        # Check for common SQL injection patterns
        dangerous_patterns = [
            r"(\bOR\b.*=.*)",
            r"(\bDROP\b)",
            r"(\bDELETE\b)",
            r"(\bINSERT\b)",
            r"(\bUPDATE\b)",
            r"(--)",
            r"(;)",
            r"(/\*)",
            r"(\*/)",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return False
        
        return True


# Convenience functions
def validate_account_number(account_number: str) -> Tuple[bool, str]:
    """Convenience function for account number validation."""
    return AccountValidator.validate_account_number(account_number)


def validate_amount(amount: float) -> Tuple[bool, str]:
    """Convenience function for amount validation."""
    return TransactionValidator.validate_amount(amount)


def validate_email(email: str) -> Tuple[bool, str]:
    """Convenience function for email validation."""
    return InputValidator.validate_email(email)
