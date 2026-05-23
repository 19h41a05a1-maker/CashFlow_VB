"""
Account endpoints for account CRUD operations and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.account_service import AccountService
from app.models.schemas import (
    AccountCreateRequest,
    AccountUpdateRequest,
    AccountResponse
)
from app.exceptions.base_exception import (
    AccountNotFoundException,
    ValidationException,
    DuplicateAccountException
)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    request: AccountCreateRequest,
    db: Session = Depends(get_db),
    user_id: int = 1  # Would come from JWT in real implementation
):
    """
    Create a new account.
    
    Args:
        request: Account creation request
        db: Database session
        user_id: User ID creating account
        
    Returns:
        AccountResponse: Created account
    """
    try:
        account_service = AccountService(db)
        account = account_service.create_account(request, created_by=user_id)
        return account
    except DuplicateAccountException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
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


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Get account details by ID.
    
    Args:
        account_id: Account ID
        db: Database session
        
    Returns:
        AccountResponse: Account details
    """
    try:
        account_service = AccountService(db)
        account = account_service.get_account(account_id)
        return account
    except AccountNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=dict)
async def list_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    List accounts with pagination.
    
    Args:
        skip: Offset for pagination
        limit: Limit for pagination
        status: Optional status filter
        db: Database session
        
    Returns:
        dict: List of accounts with pagination metadata
    """
    try:
        account_service = AccountService(db)
        accounts = account_service.list_accounts(skip=skip, limit=limit, status=status)
        
        return {
            "items": accounts,
            "skip": skip,
            "limit": limit,
            "total": len(accounts)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/search/{search_term}", response_model=dict)
async def search_accounts(
    search_term: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Search accounts by account number, customer name, or MMI ID.
    
    Args:
        search_term: Search term
        skip: Offset for pagination
        limit: Limit for pagination
        db: Database session
        
    Returns:
        dict: Matching accounts
    """
    try:
        account_service = AccountService(db)
        accounts = account_service.search_accounts(search_term, skip=skip, limit=limit)
        
        return {
            "items": accounts,
            "search_term": search_term,
            "total": len(accounts)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    request: AccountUpdateRequest,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Update account information.
    
    Args:
        account_id: Account ID
        request: Update request
        db: Database session
        user_id: User ID performing update
        
    Returns:
        AccountResponse: Updated account
    """
    try:
        account_service = AccountService(db)
        account = account_service.update_account(account_id, request, modified_by=user_id)
        return account
    except AccountNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{account_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def deactivate_account(
    account_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Deactivate an account.
    
    Args:
        account_id: Account ID
        db: Database session
        user_id: User ID performing deactivation
        
    Returns:
        dict: Deactivation response
    """
    try:
        account_service = AccountService(db)
        account = account_service.deactivate_account(account_id, modified_by=user_id)
        
        return {
            "success": True,
            "message": f"Account {account_id} has been deactivated",
            "account": account
        }
    except AccountNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{account_id}/statistics", response_model=dict)
async def get_account_statistics(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Get account statistics.
    
    Args:
        account_id: Account ID
        db: Database session
        
    Returns:
        dict: Account statistics
    """
    try:
        account_service = AccountService(db)
        stats = account_service.get_account_statistics()
        
        return {
            "account_id": account_id,
            "statistics": stats
        }
    except AccountNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
