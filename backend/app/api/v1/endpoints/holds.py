"""
Hold endpoints for managing account holds (waive, release, check status).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.hold_service import HoldService
from app.models.schemas import (
    HoldWaiverRequest,
    HoldEarlyReleaseRequest,
    HoldResponse,
    HoldDetailResponse
)
from app.exceptions.base_exception import (
    AccountNotFoundException,
    HoldNotFoundException,
    ValidationException
)

router = APIRouter(prefix="/holds", tags=["Holds"])


@router.get("", response_model=dict)
async def list_holds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    List all holds with optional status filter.
    
    Args:
        skip: Offset for pagination
        limit: Limit for pagination
        status: Optional status filter (ACTIVE, COMPLETED, WAIVED, RELEASED_EARLY)
        db: Database session
        
    Returns:
        dict: List of holds
    """
    try:
        hold_service = HoldService(db)
        
        if status:
            holds = hold_service.get_active_holds(skip=skip, limit=limit)
        else:
            holds = hold_service.get_active_holds(skip=skip, limit=limit)
        
        return {
            "items": holds,
            "skip": skip,
            "limit": limit,
            "total": len(holds),
            "status_filter": status
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{hold_id}", response_model=HoldDetailResponse)
async def get_hold(
    hold_id: str,
    db: Session = Depends(get_db)
):
    """
    Get hold details.
    
    Args:
        hold_id: Hold ID
        db: Database session
        
    Returns:
        HoldDetailResponse: Hold details
    """
    try:
        hold_service = HoldService(db)
        hold = hold_service.get_hold(hold_id)
        return hold
    except HoldNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/accounts/{account_id}/holds", response_model=dict)
async def get_account_holds(
    account_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get holds for an account.
    
    Args:
        account_id: Account ID
        skip: Offset for pagination
        limit: Limit for pagination
        status: Optional status filter
        db: Database session
        
    Returns:
        dict: List of holds for account
    """
    try:
        hold_service = HoldService(db)
        holds = hold_service.get_account_holds(account_id, skip=skip, limit=limit, status=status)
        
        return {
            "account_id": account_id,
            "items": holds,
            "skip": skip,
            "limit": limit,
            "total": len(holds)
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


@router.get("/expiring-soon", response_model=dict)
async def get_holds_expiring_soon(
    days: int = Query(1, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Get holds expiring within N days.
    
    Args:
        days: Number of days to look ahead
        db: Database session
        
    Returns:
        dict: List of holds expiring soon
    """
    try:
        hold_service = HoldService(db)
        holds = hold_service.get_holds_expiring_soon(days=days)
        
        return {
            "days_ahead": days,
            "items": holds,
            "total": len(holds)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{hold_id}/waive", response_model=HoldDetailResponse)
async def waive_hold(
    hold_id: str,
    request: HoldWaiverRequest,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Request hold waiver.
    
    Args:
        hold_id: Hold ID
        request: Waiver request with reason
        db: Database session
        user_id: User ID approving waiver
        
    Returns:
        HoldDetailResponse: Updated hold with waiver status
    """
    try:
        hold_service = HoldService(db)
        hold = hold_service.waive_hold(hold_id, request, approved_by=user_id)
        return hold
    except HoldNotFoundException as e:
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


@router.post("/{hold_id}/release-early", response_model=HoldDetailResponse)
async def release_hold_early(
    hold_id: str,
    request: HoldEarlyReleaseRequest,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    Request early hold release.
    
    Args:
        hold_id: Hold ID
        request: Release request with reason
        db: Database session
        user_id: User ID requesting release
        
    Returns:
        HoldDetailResponse: Updated hold with release status
    """
    try:
        hold_service = HoldService(db)
        hold = hold_service.request_early_release(hold_id, request, requested_by=user_id)
        return hold
    except HoldNotFoundException as e:
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


@router.get("/accounts/{account_id}/status", response_model=dict)
async def check_account_hold_status(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Check hold status for an account (used by debit service).
    
    Args:
        account_id: Account ID
        db: Database session
        
    Returns:
        dict: Hold status information
    """
    try:
        hold_service = HoldService(db)
        status_info = hold_service.check_account_hold_status(account_id)
        
        return status_info
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


@router.get("/statistics", response_model=dict)
async def get_hold_statistics(
    db: Session = Depends(get_db)
):
    """
    Get hold statistics across all accounts.
    
    Args:
        db: Database session
        
    Returns:
        dict: Hold statistics
    """
    try:
        hold_service = HoldService(db)
        stats = hold_service.get_hold_statistics()
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
