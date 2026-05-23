"""
JWT Token handling and management.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import logging

from app.config import settings
from app.exceptions.base_exception import InvalidTokenException, TokenExpiredException

logger = logging.getLogger(__name__)


class JWTHandler:
    """Handler for JWT token generation and validation."""
    
    def __init__(self):
        """Initialize JWT handler with configuration."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(
        self,
        subject: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            subject: Data to encode in token (user_id, roles, etc.)
            expires_delta: Custom expiration time
            
        Returns:
            str: Encoded JWT token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            **subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise
    
    def create_refresh_token(self, subject: Dict[str, Any]) -> str:
        """
        Create JWT refresh token.
        
        Args:
            subject: Data to encode in token
            
        Returns:
            str: Encoded JWT refresh token
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode = {
            **subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {str(e)}")
            raise
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            dict: Decoded token payload
            
        Raises:
            InvalidTokenException: If token is invalid
            TokenExpiredException: If token is expired
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning(f"Token has expired")
            raise TokenExpiredException()
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise InvalidTokenException()
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            raise InvalidTokenException()
    
    def decode_token(self, token: str, verify: bool = True) -> Optional[Dict[str, Any]]:
        """
        Decode JWT token with optional verification.
        
        Args:
            token: JWT token to decode
            verify: Whether to verify signature (default True)
            
        Returns:
            dict: Decoded token payload or None if invalid
        """
        try:
            if verify:
                return self.verify_token(token)
            else:
                return jwt.decode(
                    token,
                    options={"verify_signature": False}
                )
        except Exception as e:
            logger.warning(f"Error decoding token: {str(e)}")
            return None
    
    def get_token_expiry_time(self, token: str) -> Optional[datetime]:
        """
        Get token expiration time.
        
        Args:
            token: JWT token
            
        Returns:
            datetime: Token expiration time or None if invalid
        """
        try:
            payload = self.decode_token(token, verify=False)
            if payload and "exp" in payload:
                return datetime.fromtimestamp(payload["exp"])
        except Exception as e:
            logger.warning(f"Error getting token expiry: {str(e)}")
        return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired.
        
        Args:
            token: JWT token
            
        Returns:
            bool: True if token is expired
        """
        try:
            payload = self.decode_token(token, verify=False)
            if payload and "exp" in payload:
                expiry = datetime.fromtimestamp(payload["exp"])
                return datetime.utcnow() > expiry
        except Exception:
            return True
        return False
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            str: New access token or None if refresh token invalid
        """
        try:
            payload = self.verify_token(refresh_token)
            if payload.get("type") != "refresh":
                logger.warning("Invalid refresh token type")
                return None
            
            # Remove old exp and type, set new ones
            subject = {k: v for k, v in payload.items() if k not in ["exp", "iat", "type"]}
            return self.create_access_token(subject)
        except Exception as e:
            logger.warning(f"Error refreshing token: {str(e)}")
            return None


# Global JWT handler instance
jwt_handler = JWTHandler()
