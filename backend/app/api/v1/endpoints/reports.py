"""
Report endpoints for generating business reports and analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database.db import get_db
from app.services.report_service import ReportService
from app.exceptions.base_exception import AccountNotFoundException

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/account-status", response_model=dict)
async def get_account_status_report(
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate account status report.
    
    Args:
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        db: Database session
        
    Returns:
        dict: Account status report
    """
    try:
        report_service = ReportService(db)
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        report = report_service.generate_account_status_report(start, end)
        return report
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


@router.get("/hold-status", response_model=dict)
async def get_hold_status_report(
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate hold status report.
    
    Args:
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        db: Database session
        
    Returns:
        dict: Hold status report
    """
    try:
        report_service = ReportService(db)
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        report = report_service.generate_hold_status_report(start, end)
        return report
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


@router.get("/debit-processing", response_model=dict)
async def get_debit_processing_report(
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate debit processing report.
    
    Args:
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        db: Database session
        
    Returns:
        dict: Debit processing report
    """
    try:
        report_service = ReportService(db)
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        report = report_service.generate_debit_processing_report(start, end)
        return report
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


@router.get("/compliance", response_model=dict)
async def get_compliance_report(
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate compliance report.
    
    Args:
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        db: Database session
        
    Returns:
        dict: Compliance report
    """
    try:
        report_service = ReportService(db)
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        report = report_service.generate_compliance_report(start, end)
        return report
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


@router.get("/transaction-history/{account_id}", response_model=dict)
async def get_transaction_history_report(
    account_id: int,
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate transaction history report for an account.
    
    Args:
        account_id: Account ID
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        db: Database session
        
    Returns:
        dict: Transaction history report
    """
    try:
        report_service = ReportService(db)
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        report = report_service.generate_transaction_history_report(account_id, start, end)
        return report
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


@router.get("/hold-analytics", response_model=dict)
async def get_hold_analytics_report(
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate hold analytics report.
    
    Args:
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        db: Database session
        
    Returns:
        dict: Hold analytics report
    """
    try:
        report_service = ReportService(db)
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        report = report_service.generate_hold_analytics_report(start, end)
        return report
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
