"""
Authentication endpoints for user login, registration, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.auth_service import AuthService
from app.models.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.exceptions.base_exception import (
    InvalidCredentialsException,
    ValidationException,
    AccountLockedException
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        request: Registration request with username, email, password
        db: Database session
        
    Returns:
        dict: User creation response
        
    Raises:
        HTTPException: If validation fails or user already exists
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.register_user(request)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return tokens.
    
    Args:
        request: Login credentials
        db: Database session
        
    Returns:
        TokenResponse: Access and refresh tokens
        
    Raises:
        HTTPException: If credentials invalid or account locked
    """
    try:
        auth_service = AuthService(db)
        token_response = auth_service.login(request)
        return token_response
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except AccountLockedException as e:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked until {e.locked_until}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/logout", response_model=dict)
async def logout(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Logout user and invalidate session.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        dict: Logout response
    """
    try:
        auth_service = AuthService(db)
        success, message = auth_service.logout(user_id)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Refresh token
        db: Database session
        
    Returns:
        TokenResponse: New tokens
        
    Raises:
        HTTPException: If token invalid or expired
    """
    try:
        auth_service = AuthService(db)
        token_response = auth_service.refresh_access_token(refresh_token)
        return token_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Request password reset.
    
    Args:
        email: User email
        db: Database session
        
    Returns:
        dict: Response message
    """
    try:
        auth_service = AuthService(db)
        success, message = auth_service.request_password_reset(email)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/reset-password", response_model=dict)
async def reset_password(
    email: str,
    reset_token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    Reset password using reset token.
    
    Args:
        email: User email
        reset_token: Password reset token
        new_password: New password
        db: Database session
        
    Returns:
        dict: Response message
    """
    try:
        auth_service = AuthService(db)
        success, message = auth_service.reset_password(email, reset_token, new_password)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
