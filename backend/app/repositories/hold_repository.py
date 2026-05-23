"""
Hold repository for hold data access.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging

from app.database.models import Hold, HoldStatusEnum
from app.repositories.base_repository import BaseRepository
from app.exceptions.base_exception import (
    HoldNotFoundException,
    DatabaseException
)

logger = logging.getLogger(__name__)


class HoldRepository(BaseRepository[Hold]):
    """Repository for hold operations."""
    
    def __init__(self, db: Session):
        """Initialize hold repository."""
        super().__init__(db, Hold)
    
    def get_by_hold_id(self, hold_id: str) -> Optional[Hold]:
        """
        Get hold by hold ID.
        
        Args:
            hold_id: Hold ID to search
            
        Returns:
            Hold: Hold object or None if not found
        """
        try:
            return self.db.query(Hold).filter(
                Hold.hold_id == hold_id,
                Hold.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"Error getting hold by ID: {str(e)}")
            raise DatabaseException("Failed to get hold", e)
    
    def get_account_holds(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Hold]:
        """
        Get holds for an account.
        
        Args:
            account_id: Account ID
            skip: Offset for pagination
            limit: Limit for pagination
            status: Optional status filter
            
        Returns:
            List[Hold]: List of holds for account
        """
        try:
            query = self.db.query(Hold).filter(
                Hold.account_id == account_id,
                Hold.is_deleted == False
            )
            
            if status:
                query = query.filter(Hold.hold_status == status)
            
            return query.order_by(Hold.hold_expiry_date.asc()).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting account holds: {str(e)}")
            raise DatabaseException("Failed to get holds", e)
    
    def get_active_holds(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Hold]:
        """
        Get all active holds across all accounts.
        
        Args:
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[Hold]: List of active holds
        """
        try:
            return self.db.query(Hold).filter(
                Hold.hold_status == HoldStatusEnum.ACTIVE.value,
                Hold.is_deleted == False
            ).order_by(Hold.hold_expiry_date.asc()).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting active holds: {str(e)}")
            raise DatabaseException("Failed to get holds", e)
    
    def get_expired_holds(self) -> List[Hold]:
        """
        Get holds that have expired (expiry_date <= now).
        
        Returns:
            List[Hold]: List of expired holds
        """
        try:
            now = datetime.utcnow()
            return self.db.query(Hold).filter(
                Hold.hold_status == HoldStatusEnum.ACTIVE.value,
                Hold.hold_expiry_date <= now,
                Hold.is_deleted == False
            ).all()
        except Exception as e:
            logger.error(f"Error getting expired holds: {str(e)}")
            raise DatabaseException("Failed to get expired holds", e)
    
    def get_holds_expiring_soon(self, days: int = 1) -> List[Hold]:
        """
        Get holds expiring within N days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List[Hold]: List of holds expiring soon
        """
        try:
            now = datetime.utcnow()
            future_date = datetime.utcnow() + self.db.func.coalesce(
                self.db.literal(days * 86400), 86400
            )
            
            # Simplified version without interval arithmetic
            from datetime import timedelta
            future = now + timedelta(days=days)
            
            return self.db.query(Hold).filter(
                Hold.hold_status == HoldStatusEnum.ACTIVE.value,
                Hold.hold_expiry_date > now,
                Hold.hold_expiry_date <= future,
                Hold.is_deleted == False
            ).order_by(Hold.hold_expiry_date.asc()).all()
        except Exception as e:
            logger.error(f"Error getting holds expiring soon: {str(e)}")
            raise DatabaseException("Failed to get holds", e)
    
    def get_hold_by_credit_transaction(self, credit_transaction_id: int) -> Optional[Hold]:
        """
        Get hold created for a specific credit transaction.
        
        Args:
            credit_transaction_id: Credit transaction ID
            
        Returns:
            Hold: Hold object or None if not found
        """
        try:
            return self.db.query(Hold).filter(
                Hold.credit_transaction_id == credit_transaction_id,
                Hold.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"Error getting hold by transaction: {str(e)}")
            raise DatabaseException("Failed to get hold", e)
    
    def create_hold(
        self,
        hold_id: str,
        credit_transaction_id: int,
        account_id: int,
        hold_amount: float,
        hold_start_date: datetime,
        hold_expiry_date: datetime,
        created_by: int,
        hold_reason: Optional[str] = None,
        business_days_count: int = 5,
        **kwargs
    ) -> Hold:
        """
        Create a new hold.
        
        Args:
            hold_id: Unique hold ID
            credit_transaction_id: Credit transaction ID
            account_id: Account ID
            hold_amount: Amount being held
            hold_start_date: When hold started
            hold_expiry_date: When hold expires
            created_by: User ID who created
            hold_reason: Reason for hold
            business_days_count: Number of business days
            **kwargs: Additional attributes
            
        Returns:
            Hold: Created hold object
        """
        try:
            hold = Hold(
                hold_id=hold_id,
                credit_transaction_id=credit_transaction_id,
                account_id=account_id,
                hold_amount=hold_amount,
                hold_start_date=hold_start_date,
                hold_expiry_date=hold_expiry_date,
                hold_status=HoldStatusEnum.ACTIVE.value,
                hold_reason=hold_reason,
                business_days_count=business_days_count,
                created_by=created_by,
                **kwargs
            )
            self.db.add(hold)
            self.db.commit()
            self.db.refresh(hold)
            logger.info(f"Hold created: {hold_id}")
            return hold
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating hold: {str(e)}")
            raise DatabaseException("Failed to create hold", e)
    
    def mark_hold_completed(self, hold_id_str: str) -> Optional[Hold]:
        """
        Mark hold as completed.
        
        Args:
            hold_id_str: Hold ID
            
        Returns:
            Hold: Updated hold object
        """
        try:
            hold = self.get_by_hold_id(hold_id_str)
            if not hold:
                raise HoldNotFoundException(hold_id_str)
            
            hold.hold_status = HoldStatusEnum.COMPLETED.value
            hold.modified_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(hold)
            logger.info(f"Hold marked completed: {hold_id_str}")
            return hold
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking hold completed: {str(e)}")
            raise DatabaseException("Failed to mark hold completed", e)
    
    def waive_hold(
        self,
        hold_id_str: str,
        waiver_reason: str,
        waiver_by: int
    ) -> Optional[Hold]:
        """
        Waive a hold.
        
        Args:
            hold_id_str: Hold ID
            waiver_reason: Reason for waiver
            waiver_by: User ID who approved waiver
            
        Returns:
            Hold: Updated hold object
        """
        try:
            hold = self.get_by_hold_id(hold_id_str)
            if not hold:
                raise HoldNotFoundException(hold_id_str)
            
            hold.hold_status = HoldStatusEnum.WAIVED.value
            hold.waiver_reason = waiver_reason
            hold.waiver_by = waiver_by
            hold.waiver_at = datetime.utcnow()
            hold.modified_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(hold)
            logger.info(f"Hold waived: {hold_id_str}")
            return hold
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error waiving hold: {str(e)}")
            raise DatabaseException("Failed to waive hold", e)
    
    def release_hold_early(
        self,
        hold_id_str: str,
        release_reason: str,
        release_by: int
    ) -> Optional[Hold]:
        """
        Release hold early.
        
        Args:
            hold_id_str: Hold ID
            release_reason: Reason for early release
            release_by: User ID who approved release
            
        Returns:
            Hold: Updated hold object
        """
        try:
            hold = self.get_by_hold_id(hold_id_str)
            if not hold:
                raise HoldNotFoundException(hold_id_str)
            
            hold.hold_status = HoldStatusEnum.RELEASED_EARLY.value
            hold.early_release_reason = release_reason
            hold.early_release_by = release_by
            hold.early_release_at = datetime.utcnow()
            hold.modified_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(hold)
            logger.info(f"Hold released early: {hold_id_str}")
            return hold
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error releasing hold early: {str(e)}")
            raise DatabaseException("Failed to release hold", e)
    
    def get_hold_statistics(self) -> Dict[str, Any]:
        """
        Get hold statistics.
        
        Returns:
            Dict: Statistics about holds
        """
        try:
            total_holds = self.db.query(Hold).filter(
                Hold.is_deleted == False
            ).count()
            
            active_holds = self.db.query(Hold).filter(
                Hold.hold_status == HoldStatusEnum.ACTIVE.value,
                Hold.is_deleted == False
            ).count()
            
            total_hold_amount = self.db.query(Hold).filter(
                Hold.hold_status == HoldStatusEnum.ACTIVE.value,
                Hold.is_deleted == False
            ).with_entities(
                func.sum(Hold.hold_amount)
            ).scalar() or 0
            
            completed_holds = self.db.query(Hold).filter(
                Hold.hold_status == HoldStatusEnum.COMPLETED.value,
                Hold.is_deleted == False
            ).count()
            
            waived_holds = self.db.query(Hold).filter(
                Hold.hold_status == HoldStatusEnum.WAIVED.value,
                Hold.is_deleted == False
            ).count()
            
            return {
                "total_holds": total_holds,
                "active_holds": active_holds,
                "completed_holds": completed_holds,
                "waived_holds": waived_holds,
                "total_hold_amount": float(total_hold_amount)
            }
        except Exception as e:
            logger.error(f"Error getting hold statistics: {str(e)}")
            raise DatabaseException("Failed to get statistics", e)
