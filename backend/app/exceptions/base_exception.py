"""
Custom exception classes for business logic and error handling.
"""

from typing import Optional, List, Dict, Any


class BaseException(Exception):
    """Base exception class for all custom exceptions."""
    
    def __init__(
        self,
        message: str,
        code: str = "ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base exception.
        
        Args:
            message: Error message
            code: Error code for identification
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(BaseException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        """
        Initialize validation exception.
        
        Args:
            message: Error message
            field: Field that failed validation
            details: Additional details
        """
        exc_details = {"field": field} if field else {}
        if details:
            exc_details.update(details)
        
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=exc_details
        )


class AccountNotFoundException(BaseException):
    """Raised when account is not found."""
    
    def __init__(self, account_id: Optional[int] = None, account_number: Optional[str] = None):
        """
        Initialize account not found exception.
        
        Args:
            account_id: Account ID that was searched
            account_number: Account number that was searched
        """
        details = {}
        if account_id:
            details["account_id"] = account_id
        if account_number:
            details["account_number"] = account_number
        
        super().__init__(
            message="Account not found",
            code="ACCOUNT_NOT_FOUND",
            status_code=404,
            details=details
        )


class DuplicateAccountException(BaseException):
    """Raised when trying to create duplicate account."""
    
    def __init__(self, account_number: str):
        """
        Initialize duplicate account exception.
        
        Args:
            account_number: Account number that already exists
        """
        super().__init__(
            message=f"Account with number {account_number} already exists",
            code="DUPLICATE_ACCOUNT",
            status_code=409,
            details={"account_number": account_number}
        )


class InsufficientFundsException(BaseException):
    """Raised when account doesn't have sufficient funds."""
    
    def __init__(self, available: float, required: float):
        """
        Initialize insufficient funds exception.
        
        Args:
            available: Available balance
            required: Required amount
        """
        super().__init__(
            message=f"Insufficient funds. Available: {available}, Required: {required}",
            code="INSUFFICIENT_FUNDS",
            status_code=400,
            details={"available": available, "required": required}
        )


class HoldPeriodActiveException(BaseException):
    """Raised when trying to process debit during active hold period."""
    
    def __init__(self, hold_expiry_date: str, days_remaining: int):
        """
        Initialize hold period active exception.
        
        Args:
            hold_expiry_date: Date when hold expires
            days_remaining: Number of days remaining in hold
        """
        super().__init__(
            message=f"Cannot process debit. Credit hold period active until {hold_expiry_date}",
            code="HOLD_PERIOD_ACTIVE",
            status_code=400,
            details={
                "hold_expiry_date": hold_expiry_date,
                "days_remaining": days_remaining
            }
        )


class InvalidTransactionException(BaseException):
    """Raised when transaction is invalid."""
    
    def __init__(self, message: str, reason: Optional[str] = None):
        """
        Initialize invalid transaction exception.
        
        Args:
            message: Error message
            reason: Detailed reason
        """
        details = {"reason": reason} if reason else {}
        super().__init__(
            message=message,
            code="INVALID_TRANSACTION",
            status_code=400,
            details=details
        )


class InvalidAmountException(BaseException):
    """Raised when amount is invalid."""
    
    def __init__(self, amount: float, message: Optional[str] = None):
        """
        Initialize invalid amount exception.
        
        Args:
            amount: Invalid amount
            message: Custom error message
        """
        super().__init__(
            message=message or f"Invalid amount: {amount}",
            code="INVALID_AMOUNT",
            status_code=422,
            details={"amount": amount}
        )


class InvalidAccountStatusException(BaseException):
    """Raised when account status is invalid for operation."""
    
    def __init__(self, current_status: str, required_status: str):
        """
        Initialize invalid account status exception.
        
        Args:
            current_status: Current account status
            required_status: Required status for operation
        """
        super().__init__(
            message=f"Account status {current_status} is invalid for this operation. Required: {required_status}",
            code="INVALID_ACCOUNT_STATUS",
            status_code=400,
            details={
                "current_status": current_status,
                "required_status": required_status
            }
        )


class HoldNotFoundException(BaseException):
    """Raised when hold is not found."""
    
    def __init__(self, hold_id: Optional[str] = None):
        """
        Initialize hold not found exception.
        
        Args:
            hold_id: Hold ID that was searched
        """
        super().__init__(
            message="Hold not found",
            code="HOLD_NOT_FOUND",
            status_code=404,
            details={"hold_id": hold_id} if hold_id else {}
        )


class DebitRequestNotFoundException(BaseException):
    """Raised when debit request is not found."""
    
    def __init__(self, debit_id: Optional[str] = None):
        """
        Initialize debit request not found exception.
        
        Args:
            debit_id: Debit request ID that was searched
        """
        super().__init__(
            message="Debit request not found",
            code="DEBIT_REQUEST_NOT_FOUND",
            status_code=404,
            details={"debit_id": debit_id} if debit_id else {}
        )


class AuthenticationException(BaseException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        """
        Initialize authentication exception.
        
        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=401,
        )


class InvalidCredentialsException(AuthenticationException):
    """Raised when credentials are invalid."""
    
    def __init__(self):
        """Initialize invalid credentials exception."""
        super().__init__("Invalid username or password")


class TokenExpiredException(AuthenticationException):
    """Raised when token has expired."""
    
    def __init__(self):
        """Initialize token expired exception."""
        super().__init__("Token has expired")


class InvalidTokenException(AuthenticationException):
    """Raised when token is invalid."""
    
    def __init__(self):
        """Initialize invalid token exception."""
        super().__init__("Invalid or malformed token")


class AccountLockedException(AuthenticationException):
    """Raised when account is locked due to failed login attempts."""
    
    def __init__(self, locked_until: str):
        """
        Initialize account locked exception.
        
        Args:
            locked_until: Timestamp until which account is locked
        """
        super().__init__(f"Account is locked until {locked_until}")


class AuthorizationException(BaseException):
    """Raised when user doesn't have required permissions."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        """
        Initialize authorization exception.
        
        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            code="AUTHORIZATION_FAILED",
            status_code=403,
        )


class UserNotFoundException(BaseException):
    """Raised when user is not found."""
    
    def __init__(self, user_id: Optional[int] = None, username: Optional[str] = None):
        """
        Initialize user not found exception.
        
        Args:
            user_id: User ID that was searched
            username: Username that was searched
        """
        details = {}
        if user_id:
            details["user_id"] = user_id
        if username:
            details["username"] = username
        
        super().__init__(
            message="User not found",
            code="USER_NOT_FOUND",
            status_code=404,
            details=details
        )


class DatabaseException(BaseException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Initialize database exception.
        
        Args:
            message: Error message
            original_error: Original exception
        """
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details=details
        )


class ExternalServiceException(BaseException):
    """Raised when external service call fails."""
    
    def __init__(self, service_name: str, message: str, status_code: int = 502):
        """
        Initialize external service exception.
        
        Args:
            service_name: Name of external service
            message: Error message
            status_code: HTTP status code
        """
        super().__init__(
            message=f"{service_name} service error: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=status_code,
            details={"service_name": service_name}
        )


class ConfigurationException(BaseException):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        """
        Initialize configuration exception.
        
        Args:
            message: Error message
            config_key: Configuration key that is invalid
        """
        details = {}
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details=details
        )


class BusinessRuleException(BaseException):
    """Raised when business rule is violated."""
    
    def __init__(self, message: str, rule_name: Optional[str] = None):
        """
        Initialize business rule exception.
        
        Args:
            message: Error message
            rule_name: Name of the violated rule
        """
        details = {}
        if rule_name:
            details["rule_name"] = rule_name
        
        super().__init__(
            message=message,
            code="BUSINESS_RULE_VIOLATION",
            status_code=400,
            details=details
        )
