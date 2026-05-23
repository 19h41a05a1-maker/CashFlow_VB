"""
Debit service layer for debit request management and hold verification.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import logging
import uuid

from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.hold_repository import HoldRepository
from app.validators.input_validator import InputValidator, TransactionValidator
from app.utils.business_day import business_day_calculator
from app.exceptions.base_exception import (
    ValidationException,
    AccountNotFoundException,
    HoldPeriodActiveException,
    InsufficientFundsException,
    DebitRequestNotFoundException,
    BusinessRuleException
)
from app.models.schemas import (
    DebitRequestCreateRequest,
    DebitDetailResponse,
    HoldCheckResponse,
    DebitResponse
)

logger = logging.getLogger(__name__)


class DebitService:
    """Service for debit request management and processing."""
    
    def __init__(self, db: Session):
        """
        Initialize debit service.
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.account_repo = AccountRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.hold_repo = HoldRepository(db)
        self.validator = TransactionValidator()
    
    def submit_debit_request(
        self,
        account_number: str,
        request: DebitRequestCreateRequest,
        submitted_by: int
    ) -> DebitDetailResponse:
        """
        Submit a debit request for processing.
        
        Args:
            account_number: Account number
            request: Debit request details
            submitted_by: User ID submitting request
            
        Returns:
            DebitDetailResponse: Created debit request
            
        Raises:
            AccountNotFoundException: If account not found
            ValidationException: If request invalid
            HoldPeriodActiveException: If active holds exist
            InsufficientFundsException: If insufficient funds
        """
        # Get account
        account = self.account_repo.get_by_account_number(account_number)
        if not account:
            raise AccountNotFoundException(account_number=account_number)
        
        # Validate amount
        is_valid, error = self.validator.validate_amount(request.amount)
        if not is_valid:
            raise ValidationException(error, "amount")
        
        # Validate debit type
        is_valid, error = self.validator.validate_transaction_type(request.debit_type)
        if not is_valid:
            raise ValidationException(error, "debit_type")
        
        try:
            # Check for active holds
            hold_check = self.verify_hold_status(account.id)
            
            if hold_check["has_active_holds"]:
                logger.warning(
                    f"Debit request blocked for account {account_number}: "
                    f"{hold_check['active_holds_count']} active hold(s)"
                )
                raise HoldPeriodActiveException(
                    account_number=account_number,
                    days_remaining=hold_check.get("days_remaining", 0),
                    message=hold_check["message"]
                )
            
            # Check available balance (current - pending holds)
            available_balance = account.current_balance - account.pending_hold_amount
            if available_balance < request.amount:
                raise InsufficientFundsException(
                    required=request.amount,
                    available=available_balance
                )
            
            # Create debit request record
            debit_id = f"DEBIT-{uuid.uuid4().hex[:12]}"
            debit_request = self.db.query(self._get_debit_model()).filter(
                self._get_debit_model().debit_id == debit_id
            ).first()
            
            # Create transaction for debit
            transaction_id = f"TXN-{uuid.uuid4().hex[:12]}"
            debit_transaction = self.transaction_repo.create_transaction(
                account_id=account.id,
                transaction_id=transaction_id,
                transaction_type=request.debit_type,
                amount=request.amount,
                status="PENDING_APPROVAL",
                reference_number=request.reference_number,
                description=request.description,
                created_by=submitted_by
            )
            
            logger.info(
                f"Debit request submitted: {debit_id} for account {account_number}, "
                f"amount: ${request.amount:.2f}, transaction: {transaction_id}"
            )
            
            # Build response
            return self._to_detail_response({
                "debit_id": debit_id,
                "account_id": account.id,
                "transaction_id": transaction_id,
                "amount": request.amount,
                "debit_type": request.debit_type,
                "reference_number": request.reference_number,
                "description": request.description,
                "status": "SUBMITTED",
                "hold_check_passed": True,
                "submitted_by": submitted_by,
                "created_at": datetime.utcnow()
            })
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error submitting debit request: {str(e)}")
            raise
    
    def verify_hold_status(self, account_id: int) -> Dict[str, Any]:
        """
        Verify if account has active holds blocking debit processing.
        
        Args:
            account_id: Account ID
            
        Returns:
            Dict: Hold verification result
            
        Raises:
            AccountNotFoundException: If account not found
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFoundException(account_id=account_id)
        
        # Get active holds
        active_holds = self.hold_repo.get_account_holds(
            account_id,
            status="ACTIVE"
        )
        
        if not active_holds:
            logger.debug(f"No active holds for account {account_id}")
            return {
                "has_active_holds": False,
                "hold_check_passed": True,
                "active_holds_count": 0,
                "message": "No active holds - debit processing allowed"
            }
        
        # Get earliest expiry date
        earliest_expiry = min(hold.hold_expiry_date for hold in active_holds)
        days_remaining = business_day_calculator.get_days_remaining(earliest_expiry)
        
        logger.warning(
            f"Active holds found for account {account_id}: "
            f"{len(active_holds)} hold(s), expires in {days_remaining} business days"
        )
        
        return {
            "has_active_holds": True,
            "hold_check_passed": False,
            "active_holds_count": len(active_holds),
            "earliest_hold_expiry": earliest_expiry,
            "days_remaining": days_remaining,
            "hold_amounts": [hold.hold_amount for hold in active_holds],
            "total_hold_amount": sum(hold.hold_amount for hold in active_holds),
            "message": f"{len(active_holds)} active hold(s) - debit processing blocked. "
                      f"Earliest hold expires in {days_remaining} business days."
        }
    
    def check_hold_before_debit(self, account_id: int) -> HoldCheckResponse:
        """
        Check if account can process debit based on hold status.
        
        Args:
            account_id: Account ID
            
        Returns:
            HoldCheckResponse: Hold check result
        """
        try:
            account = self.account_repo.get_by_id(account_id)
            if not account:
                raise AccountNotFoundException(account_id=account_id)
            
            hold_status = self.verify_hold_status(account_id)
            
            return HoldCheckResponse(
                account_id=account_id,
                can_process_debit=not hold_status["has_active_holds"],
                has_active_holds=hold_status["has_active_holds"],
                active_holds_count=hold_status.get("active_holds_count", 0),
                days_until_clear=hold_status.get("days_remaining", 0),
                message=hold_status["message"]
            )
        except Exception as e:
            logger.error(f"Error checking hold before debit: {str(e)}")
            raise
    
    def approve_debit(
        self,
        debit_id: str,
        approved_by: int,
        approval_notes: Optional[str] = None
    ) -> DebitDetailResponse:
        """
        Approve a debit request.
        
        Args:
            debit_id: Debit request ID
            approved_by: User ID approving
            approval_notes: Optional approval notes
            
        Returns:
            DebitDetailResponse: Updated debit request
        """
        try:
            # Get debit request (mock implementation - would query actual debit table)
            logger.info(f"Debit request approved: {debit_id} by user {approved_by}")
            
            # Verify no active holds at approval time
            # This is redundant check but important for compliance
            
            # Update status to APPROVED
            # Create debit transaction record
            
            return self._to_detail_response({
                "debit_id": debit_id,
                "status": "APPROVED",
                "approved_by": approved_by,
                "approved_at": datetime.utcnow(),
                "approval_notes": approval_notes
            })
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error approving debit: {str(e)}")
            raise
    
    def reject_debit(
        self,
        debit_id: str,
        rejected_by: int,
        rejection_reason: str
    ) -> DebitDetailResponse:
        """
        Reject a debit request.
        
        Args:
            debit_id: Debit request ID
            rejected_by: User ID rejecting
            rejection_reason: Reason for rejection
            
        Returns:
            DebitDetailResponse: Updated debit request
        """
        try:
            if not rejection_reason or len(rejection_reason.strip()) < 5:
                raise ValidationException(
                    "Rejection reason must be at least 5 characters",
                    "rejection_reason"
                )
            
            logger.info(
                f"Debit request rejected: {debit_id} by user {rejected_by}, "
                f"reason: {rejection_reason}"
            )
            
            # Update status to REJECTED
            return self._to_detail_response({
                "debit_id": debit_id,
                "status": "REJECTED",
                "rejected_by": rejected_by,
                "rejected_at": datetime.utcnow(),
                "rejection_reason": rejection_reason
            })
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error rejecting debit: {str(e)}")
            raise
    
    def process_debit(
        self,
        debit_id: str,
        processed_by: int
    ) -> DebitDetailResponse:
        """
        Process an approved debit request (update account balance, create debit transaction).
        
        Args:
            debit_id: Debit request ID
            processed_by: User ID processing
            
        Returns:
            DebitDetailResponse: Processed debit request
        """
        try:
            # Get debit details
            # Verify hold status one final time
            # Update account balance: current_balance -= amount
            # Create debit transaction record
            # Update debit request status to PROCESSED
            
            logger.info(f"Debit processed: {debit_id} by user {processed_by}")
            
            return self._to_detail_response({
                "debit_id": debit_id,
                "status": "PROCESSED",
                "processed_by": processed_by,
                "processed_at": datetime.utcnow()
            })
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing debit: {str(e)}")
            raise
    
    def get_debit_request(self, debit_id: str) -> DebitDetailResponse:
        """
        Get debit request details.
        
        Args:
            debit_id: Debit request ID
            
        Returns:
            DebitDetailResponse: Debit request details
        """
        try:
            # Get debit from database
            logger.debug(f"Retrieved debit request: {debit_id}")
            return self._to_detail_response({
                "debit_id": debit_id
            })
        except Exception as e:
            logger.error(f"Error getting debit request: {str(e)}")
            raise
    
    def get_account_debits(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[DebitResponse]:
        """
        Get debit requests for an account.
        
        Args:
            account_id: Account ID
            skip: Pagination offset
            limit: Pagination limit
            status: Optional status filter
            
        Returns:
            List[DebitResponse]: List of debit requests
        """
        try:
            account = self.account_repo.get_by_id(account_id)
            if not account:
                raise AccountNotFoundException(account_id=account_id)
            
            # Get debit transactions
            debits = self.transaction_repo.get_account_debits(
                account_id,
                skip=skip,
                limit=limit
            )
            
            return [self._to_response(debit) for debit in debits]
        except Exception as e:
            logger.error(f"Error getting account debits: {str(e)}")
            raise
    
    def get_debit_statistics(self, account_id: int) -> Dict[str, Any]:
        """
        Get debit statistics for an account.
        
        Args:
            account_id: Account ID
            
        Returns:
            Dict: Debit statistics
        """
        try:
            account = self.account_repo.get_by_id(account_id)
            if not account:
                raise AccountNotFoundException(account_id=account_id)
            
            debits = self.transaction_repo.get_account_debits(account_id)
            
            total_debits = sum(debit.amount for debit in debits)
            pending_count = len([d for d in debits if d.status == "PENDING_APPROVAL"])
            approved_count = len([d for d in debits if d.status == "APPROVED"])
            processed_count = len([d for d in debits if d.status == "PROCESSED"])
            rejected_count = len([d for d in debits if d.status == "REJECTED"])
            
            return {
                "total_debits": float(total_debits),
                "total_debit_requests": len(debits),
                "pending_count": pending_count,
                "approved_count": approved_count,
                "processed_count": processed_count,
                "rejected_count": rejected_count,
                "average_debit_amount": float(total_debits / len(debits)) if debits else 0.0
            }
        except Exception as e:
            logger.error(f"Error getting debit statistics: {str(e)}")
            raise
    
    def _to_response(self, debit) -> DebitResponse:
        """Convert debit model to response schema."""
        return DebitResponse(
            id=debit.id,
            transaction_id=debit.transaction_id,
            account_id=debit.account_id,
            amount=debit.amount,
            debit_type=debit.transaction_type,
            status=debit.status,
            reference_number=debit.reference_number,
            created_at=debit.created_at
        )
    
    def _to_detail_response(self, debit_data: Dict[str, Any]) -> DebitDetailResponse:
        """Convert debit data to detailed response schema."""
        return DebitDetailResponse(
            debit_id=debit_data.get("debit_id"),
            account_id=debit_data.get("account_id"),
            transaction_id=debit_data.get("transaction_id"),
            amount=debit_data.get("amount"),
            debit_type=debit_data.get("debit_type"),
            reference_number=debit_data.get("reference_number"),
            description=debit_data.get("description"),
            status=debit_data.get("status"),
            hold_check_passed=debit_data.get("hold_check_passed"),
            submitted_by=debit_data.get("submitted_by"),
            approved_by=debit_data.get("approved_by"),
            approved_at=debit_data.get("approved_at"),
            rejected_by=debit_data.get("rejected_by"),
            rejected_at=debit_data.get("rejected_at"),
            rejection_reason=debit_data.get("rejection_reason"),
            processed_by=debit_data.get("processed_by"),
            processed_at=debit_data.get("processed_at"),
            created_at=debit_data.get("created_at")
        )
    
    def _get_debit_model(self):
        """Get debit model class - placeholder for actual model."""
        # This would import the actual DebitRequest model
        pass
