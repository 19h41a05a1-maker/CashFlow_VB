"""
Account service layer for business logic.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging
import uuid

from app.repositories.account_repository import AccountRepository
from app.validators.input_validator import AccountValidator, InputValidator
from app.exceptions.base_exception import (
    ValidationException,
    AccountNotFoundException,
    DuplicateAccountException,
    InvalidAccountStatusException
)
from app.models.schemas import AccountCreateRequest, AccountUpdateRequest, AccountResponse

logger = logging.getLogger(__name__)


class AccountService:
    """Service for account operations."""
    
    def __init__(self, db: Session):
        """
        Initialize account service.
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.repository = AccountRepository(db)
    
    def create_account(
        self,
        request: AccountCreateRequest,
        created_by: int
    ) -> AccountResponse:
        """
        Create a new account.
        
        Args:
            request: Account creation request
            created_by: User ID creating the account
            
        Returns:
            AccountResponse: Created account
            
        Raises:
            ValidationException: If validation fails
            DuplicateAccountException: If account already exists
        """
        # Validate account number
        is_valid, error_msg = AccountValidator.validate_account_number(
            request.account_number
        )
        if not is_valid:
            raise ValidationException(error_msg, "account_number")
        
        # Validate customer name
        is_valid, error_msg = AccountValidator.validate_customer_name(
            request.customer_name
        )
        if not is_valid:
            raise ValidationException(error_msg, "customer_name")
        
        # Validate MMI ID
        is_valid, error_msg = AccountValidator.validate_mmi_id(request.mmi_id)
        if not is_valid:
            raise ValidationException(error_msg, "mmi_id")
        
        try:
            account = self.repository.create_account(
                account_number=request.account_number,
                customer_name=request.customer_name,
                mmi_id=request.mmi_id,
                account_type=request.account_type,
                currency=request.currency,
                created_by=created_by,
                status="ACTIVE",
                current_balance=0.0,
                pending_hold_amount=0.0
            )
            
            logger.info(f"Account created: {account.account_number} by user {created_by}")
            return self._to_response(account)
        except DuplicateAccountException:
            raise
        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            raise
    
    def get_account(self, account_id: int) -> AccountResponse:
        """
        Get account by ID.
        
        Args:
            account_id: Account ID
            
        Returns:
            AccountResponse: Account details
            
        Raises:
            AccountNotFoundException: If account not found
        """
        account = self.repository.get_by_id(account_id)
        if not account:
            raise AccountNotFoundException(account_id=account_id)
        
        return self._to_response(account)
    
    def get_account_by_number(self, account_number: str) -> AccountResponse:
        """
        Get account by account number.
        
        Args:
            account_number: Account number
            
        Returns:
            AccountResponse: Account details
            
        Raises:
            AccountNotFoundException: If account not found
        """
        account = self.repository.get_by_account_number(account_number)
        if not account:
            raise AccountNotFoundException(account_number=account_number)
        
        return self._to_response(account)
    
    def list_accounts(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[AccountResponse]:
        """
        List accounts.
        
        Args:
            skip: Offset for pagination
            limit: Limit for pagination
            status: Optional status filter
            
        Returns:
            List[AccountResponse]: List of accounts
        """
        if status:
            accounts = self.repository.get_filtered(
                {"status": status},
                skip=skip,
                limit=limit
            )
        else:
            accounts = self.repository.get_all(skip=skip, limit=limit)
        
        return [self._to_response(account) for account in accounts]
    
    def update_account(
        self,
        account_id: int,
        request: AccountUpdateRequest,
        modified_by: int
    ) -> AccountResponse:
        """
        Update an account.
        
        Args:
            account_id: Account ID
            request: Update request
            modified_by: User ID modifying
            
        Returns:
            AccountResponse: Updated account
            
        Raises:
            AccountNotFoundException: If account not found
            ValidationException: If validation fails
        """
        account = self.repository.get_by_id(account_id)
        if not account:
            raise AccountNotFoundException(account_id=account_id)
        
        # Validate if provided
        if request.customer_name:
            is_valid, error_msg = AccountValidator.validate_customer_name(
                request.customer_name
            )
            if not is_valid:
                raise ValidationException(error_msg, "customer_name")
        
        if request.mmi_id:
            is_valid, error_msg = AccountValidator.validate_mmi_id(request.mmi_id)
            if not is_valid:
                raise ValidationException(error_msg, "mmi_id")
        
        try:
            updated_account = self.repository.update_account(
                account_id,
                customer_name=request.customer_name,
                mmi_id=request.mmi_id,
                account_type=request.account_type,
                status=request.status,
                modified_by=modified_by
            )
            
            logger.info(f"Account updated: {updated_account.account_number} by user {modified_by}")
            return self._to_response(updated_account)
        except Exception as e:
            logger.error(f"Error updating account: {str(e)}")
            raise
    
    def deactivate_account(
        self,
        account_id: int,
        modified_by: int
    ) -> AccountResponse:
        """
        Deactivate an account.
        
        Args:
            account_id: Account ID
            modified_by: User ID deactivating
            
        Returns:
            AccountResponse: Deactivated account
            
        Raises:
            AccountNotFoundException: If account not found
        """
        account = self.repository.get_by_id(account_id)
        if not account:
            raise AccountNotFoundException(account_id=account_id)
        
        updated_account = self.repository.deactivate_account(account_id, modified_by)
        logger.info(f"Account deactivated: {updated_account.account_number} by user {modified_by}")
        return self._to_response(updated_account)
    
    def search_accounts(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AccountResponse]:
        """
        Search accounts.
        
        Args:
            search_term: Search term
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[AccountResponse]: Search results
        """
        accounts = self.repository.search_accounts(
            search_term,
            skip=skip,
            limit=limit
        )
        return [self._to_response(account) for account in accounts]
    
    def get_account_statistics(self) -> Dict[str, Any]:
        """
        Get account statistics.
        
        Returns:
            Dict: Statistics
        """
        try:
            stats = self.repository.get_account_statistics()
            logger.debug(f"Account statistics retrieved")
            return stats
        except Exception as e:
            logger.error(f"Error getting account statistics: {str(e)}")
            raise
    
    def _to_response(self, account) -> AccountResponse:
        """Convert account model to response schema."""
        return AccountResponse(
            id=account.id,
            account_number=account.account_number,
            customer_name=account.customer_name,
            mmi_id=account.mmi_id,
            account_type=account.account_type,
            currency=account.currency,
            status=account.status,
            current_balance=account.current_balance,
            pending_hold_amount=account.pending_hold_amount,
            created_at=account.created_at,
            modified_at=account.modified_at
        )
