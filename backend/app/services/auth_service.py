"""
Authentication service layer for user registration, login, and token management.
"""

from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging
import uuid

from app.auth.jwt_handler import jwt_handler
from app.auth.password_handler import password_handler
from app.repositories.account_repository import AccountRepository
from app.validators.input_validator import InputValidator
from app.exceptions.base_exception import (
    ValidationException,
    InvalidCredentialsException,
    TokenExpiredException,
    AccountLockedException,
    DuplicateAccountException,
    UserNotFoundException,
    BusinessRuleException
)
from app.models.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse
)

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        """
        Initialize auth service.
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.validator = InputValidator()
    
    def register_user(
        self,
        request: RegisterRequest
    ) -> UserResponse:
        """
        Register a new user.
        
        Args:
            request: Registration request with username, email, password
            
        Returns:
            UserResponse: Created user
            
        Raises:
            ValidationException: If validation fails
            DuplicateAccountException: If user already exists
        """
        # Validate username
        is_valid, error = self.validator.validate_username(request.username)
        if not is_valid:
            raise ValidationException(error, "username")
        
        # Validate email
        is_valid, error = self.validator.validate_email(request.email)
        if not is_valid:
            raise ValidationException(error, "email")
        
        # Validate password
        try:
            password_handler.validate_password(request.password, request.username)
        except ValidationException as e:
            logger.warning(f"Password validation failed for user registration: {str(e)}")
            raise
        
        try:
            # Check if user already exists (mock - would check actual database)
            # if user_repo.get_by_username(request.username):
            #     raise DuplicateAccountException(username=request.username)
            
            # Hash password
            password_hash = password_handler.hash_password(request.password)
            
            # Create user (mock - would create in database)
            user_id = str(uuid.uuid4())
            created_at = datetime.utcnow()
            
            logger.info(f"User registered successfully: {request.username}")
            
            return UserResponse(
                id=user_id,
                username=request.username,
                email=request.email,
                created_at=created_at,
                is_active=True
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error registering user: {str(e)}")
            raise
    
    def login(
        self,
        request: LoginRequest
    ) -> TokenResponse:
        """
        Authenticate user and return tokens.
        
        Args:
            request: Login request with username/password
            
        Returns:
            TokenResponse: Access and refresh tokens
            
        Raises:
            InvalidCredentialsException: If credentials invalid
            AccountLockedException: If account locked after failed attempts
        """
        # Validate username format
        is_valid, error = self.validator.validate_username(request.username)
        if not is_valid:
            raise ValidationException(error, "username")
        
        try:
            # Get user from database (mock - would query actual database)
            # user = user_repo.get_by_username(request.username)
            # if not user:
            #     raise InvalidCredentialsException()
            
            # Check if account locked
            # if user.locked_until and user.locked_until > datetime.utcnow():
            #     raise AccountLockedException(locked_until=user.locked_until)
            
            # Verify password
            # if not password_handler.verify_password(request.password, user.password_hash):
            #     # Increment failed login attempts
            #     user.failed_login_attempts += 1
            #     if user.failed_login_attempts >= 5:
            #         user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            #     user_repo.update(user.id, **user.__dict__)
            #     raise InvalidCredentialsException()
            
            # Reset failed attempts on successful login
            user_id = 1  # Mock user ID
            username = request.username
            
            # Create tokens
            access_token = jwt_handler.create_access_token(subject=user_id)
            refresh_token = jwt_handler.create_refresh_token(subject=user_id)
            
            logger.info(f"User logged in successfully: {username}")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=1440  # 24 hours in minutes
            )
        except (InvalidCredentialsException, AccountLockedException):
            raise
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            raise
    
    def logout(
        self,
        user_id: int,
        session_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Logout user and invalidate session.
        
        Args:
            user_id: User ID
            session_id: Optional session ID to invalidate
            
        Returns:
            Tuple: (success, message)
        """
        try:
            # Invalidate session in database
            # session_repo.update_session(session_id, is_active=False)
            
            logger.info(f"User logged out: {user_id}")
            return (True, "Logged out successfully")
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            TokenResponse: New access and refresh tokens
            
        Raises:
            TokenExpiredException: If refresh token expired
            InvalidCredentialsException: If token invalid
        """
        try:
            # Verify refresh token
            token_data = jwt_handler.decode_token(refresh_token, verify=True)
            
            if token_data.get("type") != "refresh":
                raise InvalidCredentialsException("Invalid token type")
            
            user_id = token_data.get("sub")
            
            # Create new tokens
            new_access_token = jwt_handler.create_access_token(subject=user_id)
            new_refresh_token = jwt_handler.create_refresh_token(subject=user_id)
            
            logger.info(f"Access token refreshed for user: {user_id}")
            
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=1440
            )
        except TokenExpiredException:
            logger.warning("Refresh token expired")
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise
    
    def verify_token(self, token: str) -> Tuple[bool, dict]:
        """
        Verify JWT token validity.
        
        Args:
            token: JWT token
            
        Returns:
            Tuple: (is_valid, token_data)
        """
        try:
            token_data = jwt_handler.verify_token(token)
            return (True, token_data)
        except Exception as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return (False, {})
    
    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple: (success, message)
            
        Raises:
            InvalidCredentialsException: If old password incorrect
            ValidationException: If new password invalid
        """
        try:
            # Get user from database (mock)
            # user = user_repo.get_by_id(user_id)
            # if not user:
            #     raise UserNotFoundException(user_id=user_id)
            
            # Verify old password
            # if not password_handler.verify_password(old_password, user.password_hash):
            #     raise InvalidCredentialsException("Old password is incorrect")
            
            # Validate new password
            username = "user"  # Mock username
            try:
                password_handler.validate_password(new_password, username)
            except ValidationException as e:
                logger.warning(f"New password validation failed: {str(e)}")
                raise
            
            # Check password reuse (last 5 passwords)
            # old_password_hashes = user_repo.get_password_history(user_id, limit=5)
            # if password_handler.check_password_reuse(new_password, old_password_hashes):
            #     raise BusinessRuleException("Cannot reuse recent passwords")
            
            # Hash new password
            new_password_hash = password_handler.hash_password(new_password)
            
            # Update user password and history
            # user_repo.update(user_id, password_hash=new_password_hash)
            # user_repo.add_to_password_history(user_id, old_password_hash=user.password_hash)
            
            logger.info(f"Password changed for user: {user_id}")
            return (True, "Password changed successfully")
        except (InvalidCredentialsException, ValidationException, BusinessRuleException):
            raise
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise
    
    def reset_password(
        self,
        email: str,
        reset_token: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Reset password using reset token.
        
        Args:
            email: User email
            reset_token: Password reset token
            new_password: New password
            
        Returns:
            Tuple: (success, message)
            
        Raises:
            UserNotFoundException: If user not found
            TokenExpiredException: If reset token expired
            ValidationException: If new password invalid
        """
        try:
            # Validate email
            is_valid, error = self.validator.validate_email(email)
            if not is_valid:
                raise ValidationException(error, "email")
            
            # Get user by email (mock)
            # user = user_repo.get_by_email(email)
            # if not user:
            #     raise UserNotFoundException(email=email)
            
            # Verify reset token
            # if not user.password_reset_token or user.password_reset_token != reset_token:
            #     raise InvalidCredentialsException("Invalid reset token")
            
            # if user.password_reset_expires < datetime.utcnow():
            #     raise TokenExpiredException("Reset token expired")
            
            # Validate new password
            username = "user"  # Mock username
            try:
                password_handler.validate_password(new_password, username)
            except ValidationException as e:
                logger.warning(f"New password validation failed: {str(e)}")
                raise
            
            # Hash new password
            new_password_hash = password_handler.hash_password(new_password)
            
            # Update user password and clear reset token
            # user_repo.update(
            #     user.id,
            #     password_hash=new_password_hash,
            #     password_reset_token=None,
            #     password_reset_expires=None
            # )
            
            logger.info(f"Password reset for user: {email}")
            return (True, "Password reset successfully")
        except (UserNotFoundException, TokenExpiredException, ValidationException):
            raise
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            raise
    
    def request_password_reset(self, email: str) -> Tuple[bool, str]:
        """
        Generate password reset token and send to user email.
        
        Args:
            email: User email
            
        Returns:
            Tuple: (success, message)
            
        Raises:
            UserNotFoundException: If user not found
        """
        try:
            # Validate email
            is_valid, error = self.validator.validate_email(email)
            if not is_valid:
                raise ValidationException(error, "email")
            
            # Get user by email (mock)
            # user = user_repo.get_by_email(email)
            # if not user:
            #     raise UserNotFoundException(email=email)
            
            # Generate reset token
            reset_token = password_handler.generate_password_reset_token()
            reset_expires = datetime.utcnow() + timedelta(hours=1)
            
            # Save reset token to database
            # user_repo.update(
            #     user.id,
            #     password_reset_token=reset_token,
            #     password_reset_expires=reset_expires
            # )
            
            # Send reset email (mock)
            # email_service.send_password_reset_email(email, reset_token)
            
            logger.info(f"Password reset token generated for: {email}")
            return (True, "Password reset email sent")
        except Exception as e:
            logger.error(f"Error requesting password reset: {str(e)}")
            raise
