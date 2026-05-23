"""
Debit request repository for debit request data access operations.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.repositories.base_repository import BaseRepository
from app.database.models import DebitRequest
from app.exceptions.base_exception import (
    DebitRequestNotFoundException,
    DatabaseException
)

logger = logging.getLogger(__name__)


class DebitRequestRepository(BaseRepository[DebitRequest]):
    """Repository for debit request data access."""
    
    def __init__(self, db: Session):
        """
        Initialize debit request repository.
        
        Args:
            db: SQLAlchemy session
        """
        super().__init__(db, DebitRequest)
    
    def get_by_debit_id(self, debit_id: str) -> Optional[DebitRequest]:
        """
        Get debit request by debit ID.
        
        Args:
            debit_id: Debit request ID
            
        Returns:
            DebitRequest: Debit request object or None
        """
        try:
            debit_request = self.db.query(DebitRequest).filter(
                DebitRequest.debit_id == debit_id
            ).first()
            
            if debit_request:
                logger.debug(f"Debit request retrieved: {debit_id}")
            else:
                logger.debug(f"Debit request not found: {debit_id}")
            
            return debit_request
        except Exception as e:
            logger.error(f"Error getting debit request by ID: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_account_debit_requests(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[DebitRequest]:
        """
        Get debit requests for an account.
        
        Args:
            account_id: Account ID
            skip: Offset for pagination
            limit: Limit for pagination
            status: Optional status filter
            
        Returns:
            List[DebitRequest]: List of debit requests
        """
        try:
            query = self.db.query(DebitRequest).filter(
                DebitRequest.account_id == account_id
            )
            
            if status:
                query = query.filter(DebitRequest.debit_status == status)
            
            debit_requests = query.order_by(
                DebitRequest.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(debit_requests)} debit requests for account {account_id}")
            return debit_requests
        except Exception as e:
            logger.error(f"Error getting account debit requests: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_pending_debit_requests(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[DebitRequest]:
        """
        Get all pending debit requests.
        
        Args:
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[DebitRequest]: List of pending debit requests
        """
        try:
            debit_requests = self.db.query(DebitRequest).filter(
                DebitRequest.debit_status == "PENDING_APPROVAL"
            ).order_by(
                DebitRequest.created_at.asc()
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(debit_requests)} pending debit requests")
            return debit_requests
        except Exception as e:
            logger.error(f"Error getting pending debit requests: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_approved_debit_requests(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[DebitRequest]:
        """
        Get approved debit requests.
        
        Args:
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[DebitRequest]: List of approved debit requests
        """
        try:
            debit_requests = self.db.query(DebitRequest).filter(
                DebitRequest.debit_status == "APPROVED"
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(debit_requests)} approved debit requests")
            return debit_requests
        except Exception as e:
            logger.error(f"Error getting approved debit requests: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def create_debit_request(
        self,
        account_id: int,
        debit_id: str,
        amount: float,
        debit_type: str,
        reference_number: Optional[str],
        hold_check_passed: bool,
        created_by: int
    ) -> DebitRequest:
        """
        Create new debit request.
        
        Args:
            account_id: Account ID
            debit_id: Unique debit request ID
            amount: Debit amount
            debit_type: Type of debit
            reference_number: Optional reference number
            hold_check_passed: Whether hold check passed
            created_by: User ID creating request
            
        Returns:
            DebitRequest: Created debit request
        """
        try:
            debit_request = DebitRequest(
                account_id=account_id,
                debit_id=debit_id,
                amount=amount,
                debit_type=debit_type,
                reference_number=reference_number,
                debit_status="SUBMITTED",
                hold_check_passed=hold_check_passed,
                created_by=created_by
            )
            
            self.db.add(debit_request)
            self.db.commit()
            self.db.refresh(debit_request)
            
            logger.info(f"Debit request created: {debit_id}")
            return debit_request
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating debit request: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def approve_debit_request(
        self,
        debit_id: str,
        approved_by: int,
        approval_notes: Optional[str] = None
    ) -> DebitRequest:
        """
        Approve a debit request.
        
        Args:
            debit_id: Debit request ID
            approved_by: User ID approving
            approval_notes: Optional approval notes
            
        Returns:
            DebitRequest: Updated debit request
        """
        try:
            debit_request = self.get_by_debit_id(debit_id)
            if not debit_request:
                raise DebitRequestNotFoundException(debit_id=debit_id)
            
            debit_request.debit_status = "APPROVED"
            debit_request.approved_by = approved_by
            debit_request.approved_at = datetime.utcnow()
            debit_request.approval_notes = approval_notes
            
            self.db.commit()
            self.db.refresh(debit_request)
            
            logger.info(f"Debit request approved: {debit_id}")
            return debit_request
        except DebitRequestNotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error approving debit request: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def reject_debit_request(
        self,
        debit_id: str,
        rejected_by: int,
        rejection_reason: str
    ) -> DebitRequest:
        """
        Reject a debit request.
        
        Args:
            debit_id: Debit request ID
            rejected_by: User ID rejecting
            rejection_reason: Reason for rejection
            
        Returns:
            DebitRequest: Updated debit request
        """
        try:
            debit_request = self.get_by_debit_id(debit_id)
            if not debit_request:
                raise DebitRequestNotFoundException(debit_id=debit_id)
            
            debit_request.debit_status = "REJECTED"
            debit_request.rejected_by = rejected_by
            debit_request.rejected_at = datetime.utcnow()
            debit_request.rejection_reason = rejection_reason
            
            self.db.commit()
            self.db.refresh(debit_request)
            
            logger.info(f"Debit request rejected: {debit_id}")
            return debit_request
        except DebitRequestNotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error rejecting debit request: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def process_debit_request(
        self,
        debit_id: str,
        processed_by: int
    ) -> DebitRequest:
        """
        Mark debit request as processed.
        
        Args:
            debit_id: Debit request ID
            processed_by: User ID processing
            
        Returns:
            DebitRequest: Updated debit request
        """
        try:
            debit_request = self.get_by_debit_id(debit_id)
            if not debit_request:
                raise DebitRequestNotFoundException(debit_id=debit_id)
            
            if debit_request.debit_status != "APPROVED":
                raise DatabaseException(
                    "Only approved debit requests can be processed"
                )
            
            debit_request.debit_status = "PROCESSED"
            debit_request.processed_by = processed_by
            debit_request.processed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(debit_request)
            
            logger.info(f"Debit request processed: {debit_id}")
            return debit_request
        except (DebitRequestNotFoundException, DatabaseException):
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing debit request: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_debit_requests_by_date_range(
        self,
        account_id: int,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[DebitRequest]:
        """
        Get debit requests within a date range.
        
        Args:
            account_id: Account ID
            start_date: Start date
            end_date: End date
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[DebitRequest]: List of debit requests
        """
        try:
            debit_requests = self.db.query(DebitRequest).filter(
                DebitRequest.account_id == account_id,
                DebitRequest.created_at >= start_date,
                DebitRequest.created_at <= end_date
            ).order_by(
                DebitRequest.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            logger.debug(
                f"Retrieved {len(debit_requests)} debit requests for account {account_id} "
                f"between {start_date} and {end_date}"
            )
            return debit_requests
        except Exception as e:
            logger.error(f"Error getting debit requests by date range: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_debit_request_statistics(self, account_id: int) -> dict:
        """
        Get debit request statistics for an account.
        
        Args:
            account_id: Account ID
            
        Returns:
            dict: Statistics
        """
        try:
            debit_requests = self.db.query(DebitRequest).filter(
                DebitRequest.account_id == account_id
            ).all()
            
            total_amount = sum(dr.amount for dr in debit_requests)
            total_count = len(debit_requests)
            
            stats = {
                "total_debit_requests": total_count,
                "total_debit_amount": float(total_amount),
                "submitted_count": len([dr for dr in debit_requests if dr.debit_status == "SUBMITTED"]),
                "pending_count": len([dr for dr in debit_requests if dr.debit_status == "PENDING_APPROVAL"]),
                "approved_count": len([dr for dr in debit_requests if dr.debit_status == "APPROVED"]),
                "processed_count": len([dr for dr in debit_requests if dr.debit_status == "PROCESSED"]),
                "rejected_count": len([dr for dr in debit_requests if dr.debit_status == "REJECTED"]),
                "average_debit_amount": float(total_amount / total_count) if total_count > 0 else 0.0
            }
            
            logger.debug(f"Debit request statistics retrieved for account {account_id}")
            return stats
        except Exception as e:
            logger.error(f"Error getting debit request statistics: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
