"""
Credit service layer for credit transaction business logic.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import logging
import uuid

from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.hold_repository import HoldRepository
from app.validators.input_validator import TransactionValidator, InputValidator
from app.utils.business_day import business_day_calculator
from app.exceptions.base_exception import (
    ValidationException,
    AccountNotFoundException,
    InvalidTransactionException,
    InvalidAmountException
)
from app.models.schemas import CreditRecordRequest, CreditResponse, CreditWithHoldResponse
from app.config import settings

logger = logging.getLogger(__name__)


class CreditService:
    """Service for credit transaction operations."""
    
    def __init__(self, db: Session):
        """
        Initialize credit service.
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.account_repo = AccountRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.hold_repo = HoldRepository(db)
    
    def record_credit(
        self,
        request: CreditRecordRequest,
        created_by: int
    ) -> CreditWithHoldResponse:
        """
        Record a credit transaction and create automatic hold.
        
        Args:
            request: Credit record request
            created_by: User ID recording the credit
            
        Returns:
            CreditWithHoldResponse: Credit with hold information
            
        Raises:
            ValidationException: If validation fails
            AccountNotFoundException: If account not found
            InvalidTransactionException: If transaction is invalid
        """
        # Validate account exists
        account = self.account_repo.get_by_account_number(request.account_number)
        if not account:
            raise AccountNotFoundException(account_number=request.account_number)
        
        # Validate amount
        is_valid, error_msg = TransactionValidator.validate_amount(request.amount)
        if not is_valid:
            raise InvalidAmountException(request.amount, error_msg)
        
        # Validate transaction type
        valid_types = ["ACH_CREDIT", "CHEQUE_CREDIT", "WIRE_CREDIT", "OTHER_CREDIT"]
        is_valid, error_msg = TransactionValidator.validate_transaction_type(
            request.transaction_type,
            valid_types
        )
        if not is_valid:
            raise ValidationException(error_msg, "transaction_type")
        
        # Validate reference number if provided
        if request.reference_number:
            is_valid, error_msg = TransactionValidator.validate_reference_number(
                request.reference_number
            )
            if not is_valid:
                raise ValidationException(error_msg, "reference_number")
        
        try:
            # Create transaction
            transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            transaction = self.transaction_repo.create_transaction(
                transaction_id=transaction_id,
                account_id=account.id,
                transaction_type=request.transaction_type,
                amount=request.amount,
                transaction_date=request.credit_date,
                status="PENDING_HOLD",
                reference_number=request.reference_number,
                description=request.description,
                created_by=created_by
            )
            
            # Create hold
            hold_id = f"HOLD-{uuid.uuid4().hex[:12].upper()}"
            hold_expiry = business_day_calculator.calculate_hold_expiry_date(
                request.credit_date,
                settings.HOLD_PERIOD_DAYS
            )
            
            hold = self.hold_repo.create_hold(
                hold_id=hold_id,
                credit_transaction_id=transaction.id,
                account_id=account.id,
                hold_amount=request.amount,
                hold_start_date=request.credit_date,
                hold_expiry_date=hold_expiry,
                created_by=created_by,
                hold_reason=f"Credit Hold - {request.transaction_type}",
                business_days_count=settings.HOLD_PERIOD_DAYS
            )
            
            # Update account pending hold amount
            new_pending = account.pending_hold_amount + request.amount
            self.account_repo.update_account(
                account.id,
                pending_hold_amount=new_pending,
                modified_by=created_by
            )
            
            # Update account balance
            new_balance = account.current_balance + request.amount
            self.account_repo.update_account(
                account.id,
                current_balance=new_balance,
                modified_by=created_by
            )
            
            logger.info(
                f"Credit recorded: {transaction_id} for account {account.account_number}, "
                f"amount: {request.amount}, hold expires: {hold_expiry}"
            )
            
            return self._to_response_with_hold(transaction, hold)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording credit: {str(e)}")
            raise
    
    def get_credit(self, credit_id: int) -> CreditWithHoldResponse:
        """
        Get credit transaction details.
        
        Args:
            credit_id: Credit transaction ID
            
        Returns:
            CreditWithHoldResponse: Credit details with hold
            
        Raises:
            InvalidTransactionException: If credit not found
        """
        transaction = self.transaction_repo.get_by_id(credit_id)
        if not transaction:
            raise InvalidTransactionException("Credit transaction not found")
        
        # Get associated hold
        hold = self.hold_repo.get_hold_by_credit_transaction(credit_id)
        
        return self._to_response_with_hold(transaction, hold)
    
    def get_account_credits(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[CreditResponse]:
        """
        Get all credits for an account.
        
        Args:
            account_id: Account ID
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[CreditResponse]: List of credits
            
        Raises:
            AccountNotFoundException: If account not found
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFoundException(account_id=account_id)
        
        credits = self.transaction_repo.get_account_credits(
            account_id,
            skip=skip,
            limit=limit
        )
        
        return [self._to_response(credit) for credit in credits]
    
    def get_recent_credits(
        self,
        account_id: int,
        days: int = 5
    ) -> List[CreditWithHoldResponse]:
        """
        Get credits received in the last N days with hold info.
        
        Args:
            account_id: Account ID
            days: Number of days to look back
            
        Returns:
            List[CreditWithHoldResponse]: Recent credits with hold status
            
        Raises:
            AccountNotFoundException: If account not found
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFoundException(account_id=account_id)
        
        credits = self.transaction_repo.get_recent_credits(account_id, days=days)
        
        results = []
        for credit in credits:
            hold = self.hold_repo.get_hold_by_credit_transaction(credit.id)
            results.append(self._to_response_with_hold(credit, hold))
        
        return results
    
    def get_credits_by_date_range(
        self,
        account_id: int,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[CreditResponse]:
        """
        Get credits within a date range.
        
        Args:
            account_id: Account ID
            start_date: Start date
            end_date: End date
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[CreditResponse]: Credits in date range
        """
        credits = self.transaction_repo.get_transactions_by_date_range(
            account_id,
            start_date,
            end_date,
            skip=skip,
            limit=limit
        )
        
        # Filter for credits only
        credit_types = ["ACH_CREDIT", "CHEQUE_CREDIT", "WIRE_CREDIT", "OTHER_CREDIT"]
        credits = [c for c in credits if c.transaction_type in credit_types]
        
        return [self._to_response(credit) for credit in credits]
    
    def get_total_credits(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """
        Get total credit amount for an account.
        
        Args:
            account_id: Account ID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            float: Total credit amount
        """
        totals = self.transaction_repo.get_account_totals(
            account_id,
            start_date=start_date,
            end_date=end_date
        )
        return totals.get("total_credits", 0.0)
    
    def _to_response(self, transaction) -> CreditResponse:
        """Convert transaction model to credit response schema."""
        return CreditResponse(
            id=transaction.id,
            transaction_id=transaction.transaction_id,
            account_id=transaction.account_id,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            transaction_date=transaction.transaction_date,
            status=transaction.status,
            reference_number=transaction.reference_number,
            description=transaction.description,
            created_at=transaction.created_at
        )
    
    def _to_response_with_hold(
        self,
        transaction,
        hold: Optional[Any] = None
    ) -> CreditWithHoldResponse:
        """Convert transaction and hold to response with hold info."""
        response = CreditWithHoldResponse(
            id=transaction.id,
            transaction_id=transaction.transaction_id,
            account_id=transaction.account_id,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            transaction_date=transaction.transaction_date,
            status=transaction.status,
            reference_number=transaction.reference_number,
            description=transaction.description,
            created_at=transaction.created_at
        )
        
        if hold:
            response.hold_id = hold.hold_id
            response.hold_status = hold.hold_status
            response.hold_expiry_date = hold.hold_expiry_date
            response.days_remaining = business_day_calculator.get_days_remaining(
                hold.hold_expiry_date
            )
        
        return response
