"""
Credit endpoints for recording credits with automatic hold creation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.credit_service import CreditService
from app.models.schemas import CreditRecordRequest, CreditWithHoldResponse
from app.exceptions.base_exception import (
    AccountNotFoundException,
    ValidationException
)

router = APIRouter(prefix="/credits", tags=["Credits"])


@router.post("", response_model=CreditWithHoldResponse, status_code=status.HTTP_201_CREATED)
async def record_credit(
    request: CreditRecordRequest,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Record a credit transaction with automatic 5-day hold creation.
    
    Args:
        request: Credit record request
        db: Database session
        user_id: User ID recording credit
        
    Returns:
        CreditWithHoldResponse: Created credit with hold details
    """
    try:
        credit_service = CreditService(db)
        credit = credit_service.record_credit(request, created_by=user_id)
        return credit
    except AccountNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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


@router.get("/{credit_id}", response_model=CreditWithHoldResponse)
async def get_credit(
    credit_id: str,
    db: Session = Depends(get_db)
):
    """
    Get credit transaction details.
    
    Args:
        credit_id: Credit/transaction ID
        db: Database session
        
    Returns:
        CreditWithHoldResponse: Credit details with hold info
    """
    try:
        credit_service = CreditService(db)
        credit = credit_service.get_credit(credit_id)
        return credit
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credit {credit_id} not found"
        )


@router.get("/accounts/{account_id}/credits", response_model=dict)
async def get_account_credits(
    account_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all credits for an account.
    
    Args:
        account_id: Account ID
        skip: Offset for pagination
        limit: Limit for pagination
        db: Database session
        
    Returns:
        dict: List of credits with pagination
    """
    try:
        credit_service = CreditService(db)
        credits = credit_service.get_account_credits(account_id, skip=skip, limit=limit)
        
        return {
            "account_id": account_id,
            "items": credits,
            "skip": skip,
            "limit": limit,
            "total": len(credits)
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


@router.get("/accounts/{account_id}/recent", response_model=dict)
async def get_recent_credits(
    account_id: int,
    days: int = Query(5, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get recent credits for an account.
    
    Args:
        account_id: Account ID
        days: Number of days to look back
        db: Database session
        
    Returns:
        dict: List of recent credits
    """
    try:
        credit_service = CreditService(db)
        credits = credit_service.get_recent_credits(account_id, days=days)
        
        return {
            "account_id": account_id,
            "period_days": days,
            "items": credits,
            "total": len(credits)
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


@router.get("/accounts/{account_id}/total", response_model=dict)
async def get_total_credits(
    account_id: int,
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get total credits for an account in a period.
    
    Args:
        account_id: Account ID
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        db: Database session
        
    Returns:
        dict: Credit totals
    """
    try:
        credit_service = CreditService(db)
        
        from datetime import datetime
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        total = credit_service.get_total_credits(account_id, start=start, end=end)
        
        return {
            "account_id": account_id,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "total_credits": total
        }
    except AccountNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
