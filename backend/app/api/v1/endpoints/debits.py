"""
Debit endpoints for debit request submission and hold verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.debit_service import DebitService
from app.models.schemas import (
    DebitRequestCreateRequest,
    DebitDetailResponse,
    HoldCheckResponse
)
from app.exceptions.base_exception import (
    AccountNotFoundException,
    HoldPeriodActiveException,
    InsufficientFundsException,
    ValidationException
)

router = APIRouter(prefix="/debits", tags=["Debits"])


@router.post("", response_model=DebitDetailResponse, status_code=status.HTTP_201_CREATED)
async def submit_debit_request(
    request: DebitRequestCreateRequest,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Submit a debit request (with automatic hold verification).
    
    THIS IS THE CRITICAL ENDPOINT that blocks debits during hold period.
    
    Args:
        request: Debit request details
        db: Database session
        user_id: User ID submitting request
        
    Returns:
        DebitDetailResponse: Created debit request (if hold check passes)
        
    Raises:
        HTTPException 423: If ACTIVE holds exist
        HTTPException 422: If insufficient funds
    """
    try:
        debit_service = DebitService(db)
        debit = debit_service.submit_debit_request(
            request.account_number,
            request,
            submitted_by=user_id
        )
        return debit
    except HoldPeriodActiveException as e:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "code": "HOLD_PERIOD_ACTIVE",
                "message": e.message,
                "details": e.details
            }
        )
    except InsufficientFundsException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INSUFFICIENT_FUNDS",
                "message": e.message,
                "details": e.details
            }
        )
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


@router.get("/{debit_id}", response_model=DebitDetailResponse)
async def get_debit_request(
    debit_id: str,
    db: Session = Depends(get_db)
):
    """
    Get debit request details.
    
    Args:
        debit_id: Debit request ID
        db: Database session
        
    Returns:
        DebitDetailResponse: Debit request details
    """
    try:
        debit_service = DebitService(db)
        debit = debit_service.get_debit_request(debit_id)
        return debit
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Debit request {debit_id} not found"
        )


@router.get("/accounts/{account_id}/debits", response_model=dict)
async def get_account_debits(
    account_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get debit requests for an account.
    
    Args:
        account_id: Account ID
        skip: Offset for pagination
        limit: Limit for pagination
        status: Optional status filter
        db: Database session
        
    Returns:
        dict: List of debit requests
    """
    try:
        debit_service = DebitService(db)
        debits = debit_service.get_account_debits(account_id, skip=skip, limit=limit, status=status)
        
        return {
            "account_id": account_id,
            "items": debits,
            "skip": skip,
            "limit": limit,
            "total": len(debits)
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


@router.post("/{debit_id}/approve", response_model=DebitDetailResponse)
async def approve_debit(
    debit_id: str,
    approval_notes: str = Query(None),
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Approve a debit request.
    
    Args:
        debit_id: Debit request ID
        approval_notes: Optional approval notes
        db: Database session
        user_id: User ID approving
        
    Returns:
        DebitDetailResponse: Updated debit request
    """
    try:
        debit_service = DebitService(db)
        debit = debit_service.approve_debit(debit_id, approved_by=user_id, approval_notes=approval_notes)
        return debit
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{debit_id}/reject", response_model=DebitDetailResponse)
async def reject_debit(
    debit_id: str,
    rejection_reason: str = Query(..., min_length=5),
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Reject a debit request.
    
    Args:
        debit_id: Debit request ID
        rejection_reason: Reason for rejection
        db: Database session
        user_id: User ID rejecting
        
    Returns:
        DebitDetailResponse: Updated debit request
    """
    try:
        debit_service = DebitService(db)
        debit = debit_service.reject_debit(debit_id, rejected_by=user_id, rejection_reason=rejection_reason)
        return debit
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


@router.post("/{debit_id}/process", response_model=DebitDetailResponse)
async def process_debit(
    debit_id: str,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Process an approved debit request.
    
    Args:
        debit_id: Debit request ID
        db: Database session
        user_id: User ID processing
        
    Returns:
        DebitDetailResponse: Updated debit request
    """
    try:
        debit_service = DebitService(db)
        debit = debit_service.process_debit(debit_id, processed_by=user_id)
        return debit
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{account_id}/hold-check", response_model=HoldCheckResponse)
async def check_hold_before_debit(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if account can process debit based on hold status.
    
    CRITICAL ENDPOINT: Returns hold blocking status before debit submission.
    
    Args:
        account_id: Account ID
        db: Database session
        
    Returns:
        HoldCheckResponse: Hold verification result
    """
    try:
        debit_service = DebitService(db)
        hold_check = debit_service.check_hold_before_debit(account_id)
        return hold_check
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


@router.get("/accounts/{account_id}/statistics", response_model=dict)
async def get_debit_statistics(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Get debit statistics for an account.
    
    Args:
        account_id: Account ID
        db: Database session
        
    Returns:
        dict: Debit statistics
    """
    try:
        debit_service = DebitService(db)
        stats = debit_service.get_debit_statistics(account_id)
        
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
