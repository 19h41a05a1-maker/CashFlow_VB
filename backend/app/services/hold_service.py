"""
Hold service layer for hold management business logic.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.repositories.hold_repository import HoldRepository
from app.repositories.account_repository import AccountRepository
from app.validators.input_validator import InputValidator
from app.utils.business_day import business_day_calculator
from app.exceptions.base_exception import (
    ValidationException,
    HoldNotFoundException,
    AccountNotFoundException
)
from app.models.schemas import (
    HoldWaiverRequest,
    HoldEarlyReleaseRequest,
    HoldResponse,
    HoldDetailResponse
)

logger = logging.getLogger(__name__)


class HoldService:
    """Service for hold management operations."""
    
    def __init__(self, db: Session):
        """
        Initialize hold service.
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.hold_repo = HoldRepository(db)
        self.account_repo = AccountRepository(db)
    
    def get_hold(self, hold_id: str) -> HoldDetailResponse:
        """
        Get hold details.
        
        Args:
            hold_id: Hold ID
            
        Returns:
            HoldDetailResponse: Hold details
            
        Raises:
            HoldNotFoundException: If hold not found
        """
        hold = self.hold_repo.get_by_hold_id(hold_id)
        if not hold:
            raise HoldNotFoundException(hold_id)
        
        return self._to_detail_response(hold)
    
    def get_account_holds(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[HoldResponse]:
        """
        Get holds for an account.
        
        Args:
            account_id: Account ID
            skip: Offset for pagination
            limit: Limit for pagination
            status: Optional status filter
            
        Returns:
            List[HoldResponse]: List of holds
            
        Raises:
            AccountNotFoundException: If account not found
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFoundException(account_id=account_id)
        
        holds = self.hold_repo.get_account_holds(
            account_id,
            skip=skip,
            limit=limit,
            status=status
        )
        
        return [self._to_response(hold) for hold in holds]
    
    def get_active_holds(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[HoldResponse]:
        """
        Get all active holds.
        
        Args:
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[HoldResponse]: List of active holds
        """
        holds = self.hold_repo.get_active_holds(skip=skip, limit=limit)
        return [self._to_response(hold) for hold in holds]
    
    def get_holds_expiring_soon(
        self,
        days: int = 1
    ) -> List[HoldResponse]:
        """
        Get holds expiring within N days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List[HoldResponse]: List of holds expiring soon
        """
        holds = self.hold_repo.get_holds_expiring_soon(days=days)
        return [self._to_response(hold) for hold in holds]
    
    def waive_hold(
        self,
        hold_id: str,
        request: HoldWaiverRequest,
        approved_by: int
    ) -> HoldDetailResponse:
        """
        Request hold waiver.
        
        Args:
            hold_id: Hold ID
            request: Waiver request
            approved_by: User ID approving waiver
            
        Returns:
            HoldDetailResponse: Updated hold
            
        Raises:
            HoldNotFoundException: If hold not found
            ValidationException: If request invalid
        """
        hold = self.hold_repo.get_by_hold_id(hold_id)
        if not hold:
            raise HoldNotFoundException(hold_id)
        
        if not request.waiver_reason or len(request.waiver_reason.strip()) < 10:
            raise ValidationException(
                "Waiver reason must be at least 10 characters",
                "waiver_reason"
            )
        
        try:
            # Update hold status to waived
            updated_hold = self.hold_repo.waive_hold(
                hold_id,
                request.waiver_reason,
                approved_by
            )
            
            # Update account pending holds
            account = self.account_repo.get_by_id(updated_hold.account_id)
            if account:
                new_pending = max(0, account.pending_hold_amount - updated_hold.hold_amount)
                self.account_repo.update_account(
                    account.id,
                    pending_hold_amount=new_pending,
                    modified_by=approved_by
                )
            
            logger.info(
                f"Hold waived: {hold_id} by user {approved_by}, "
                f"reason: {request.waiver_reason}"
            )
            
            return self._to_detail_response(updated_hold)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error waiving hold: {str(e)}")
            raise
    
    def request_early_release(
        self,
        hold_id: str,
        request: HoldEarlyReleaseRequest,
        requested_by: int
    ) -> HoldDetailResponse:
        """
        Request early release of hold.
        
        Args:
            hold_id: Hold ID
            request: Early release request
            requested_by: User ID requesting release
            
        Returns:
            HoldDetailResponse: Updated hold
            
        Raises:
            HoldNotFoundException: If hold not found
            ValidationException: If request invalid
        """
        hold = self.hold_repo.get_by_hold_id(hold_id)
        if not hold:
            raise HoldNotFoundException(hold_id)
        
        if not request.early_release_reason or len(request.early_release_reason.strip()) < 10:
            raise ValidationException(
                "Release reason must be at least 10 characters",
                "early_release_reason"
            )
        
        try:
            # Update hold status to released early
            updated_hold = self.hold_repo.release_hold_early(
                hold_id,
                request.early_release_reason,
                requested_by
            )
            
            # Update account pending holds
            account = self.account_repo.get_by_id(updated_hold.account_id)
            if account:
                new_pending = max(0, account.pending_hold_amount - updated_hold.hold_amount)
                self.account_repo.update_account(
                    account.id,
                    pending_hold_amount=new_pending,
                    modified_by=requested_by
                )
            
            logger.info(
                f"Hold released early: {hold_id} by user {requested_by}, "
                f"reason: {request.early_release_reason}"
            )
            
            return self._to_detail_response(updated_hold)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error releasing hold early: {str(e)}")
            raise
    
    def auto_expire_holds(self) -> int:
        """
        Automatically expire holds that have reached their expiry date.
        
        Returns:
            int: Number of holds expired
        """
        expired_holds = self.hold_repo.get_expired_holds()
        count = 0
        
        try:
            for hold in expired_holds:
                updated_hold = self.hold_repo.mark_hold_completed(hold.hold_id)
                
                # Update account pending holds
                account = self.account_repo.get_by_id(hold.account_id)
                if account:
                    new_pending = max(0, account.pending_hold_amount - hold.hold_amount)
                    self.account_repo.update_account(
                        account.id,
                        pending_hold_amount=new_pending,
                        modified_by=0  # System user
                    )
                
                count += 1
            
            logger.info(f"Auto-expired {count} holds")
            return count
        except Exception as e:
            logger.error(f"Error auto-expiring holds: {str(e)}")
            raise
    
    def get_hold_statistics(self) -> Dict[str, Any]:
        """
        Get hold statistics.
        
        Returns:
            Dict: Statistics
        """
        try:
            stats = self.hold_repo.get_hold_statistics()
            logger.debug("Hold statistics retrieved")
            return stats
        except Exception as e:
            logger.error(f"Error getting hold statistics: {str(e)}")
            raise
    
    def check_account_hold_status(self, account_id: int) -> Dict[str, Any]:
        """
        Check hold status for an account.
        
        Args:
            account_id: Account ID
            
        Returns:
            Dict: Hold status information
            
        Raises:
            AccountNotFoundException: If account not found
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFoundException(account_id=account_id)
        
        holds = self.hold_repo.get_account_holds(
            account_id,
            status="ACTIVE"
        )
        
        if not holds:
            return {
                "has_active_holds": False,
                "active_holds_count": 0,
                "pending_hold_amount": 0.0,
                "next_hold_expiry": None,
                "message": "No active holds"
            }
        
        # Get earliest expiry
        earliest_expiry = min(hold.hold_expiry_date for hold in holds)
        days_remaining = business_day_calculator.get_days_remaining(earliest_expiry)
        
        return {
            "has_active_holds": True,
            "active_holds_count": len(holds),
            "pending_hold_amount": sum(hold.hold_amount for hold in holds),
            "next_hold_expiry": earliest_expiry,
            "days_remaining": days_remaining,
            "message": f"{len(holds)} active hold(s), earliest expires in {days_remaining} business days"
        }
    
    def _to_response(self, hold) -> HoldResponse:
        """Convert hold model to response schema."""
        days_remaining = business_day_calculator.get_days_remaining(hold.hold_expiry_date)
        
        return HoldResponse(
            id=hold.id,
            hold_id=hold.hold_id,
            account_id=hold.account_id,
            hold_amount=hold.hold_amount,
            hold_start_date=hold.hold_start_date,
            hold_expiry_date=hold.hold_expiry_date,
            hold_status=hold.hold_status,
            business_days_count=hold.business_days_count,
            days_remaining=days_remaining,
            created_at=hold.created_at
        )
    
    def _to_detail_response(self, hold) -> HoldDetailResponse:
        """Convert hold model to detailed response schema."""
        response = HoldDetailResponse(
            id=hold.id,
            hold_id=hold.hold_id,
            account_id=hold.account_id,
            credit_transaction_id=hold.credit_transaction_id,
            hold_amount=hold.hold_amount,
            hold_start_date=hold.hold_start_date,
            hold_expiry_date=hold.hold_expiry_date,
            hold_status=hold.hold_status,
            hold_reason=hold.hold_reason,
            business_days_count=hold.business_days_count,
            days_remaining=business_day_calculator.get_days_remaining(hold.hold_expiry_date),
            waiver_reason=hold.waiver_reason,
            waiver_at=hold.waiver_at,
            early_release_reason=hold.early_release_reason,
            early_release_at=hold.early_release_at,
            created_at=hold.created_at
        )
        return response
