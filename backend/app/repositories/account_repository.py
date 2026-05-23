"""
Account repository for account data access.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.database.models import Account, AccountStatusEnum
from app.repositories.base_repository import BaseRepository
from app.exceptions.base_exception import (
    AccountNotFoundException,
    DuplicateAccountException,
    DatabaseException
)

logger = logging.getLogger(__name__)


class AccountRepository(BaseRepository[Account]):
    """Repository for account operations."""
    
    def __init__(self, db: Session):
        """Initialize account repository."""
        super().__init__(db, Account)
    
    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """
        Get account by account number.
        
        Args:
            account_number: Account number to search
            
        Returns:
            Account: Account object or None if not found
        """
        try:
            return self.db.query(Account).filter(
                Account.account_number == account_number,
                Account.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"Error getting account by number: {str(e)}")
            raise DatabaseException("Failed to get account", e)
    
    def get_active_accounts(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """
        Get all active accounts.
        
        Args:
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[Account]: List of active accounts
        """
        try:
            return self.db.query(Account).filter(
                Account.status == AccountStatusEnum.ACTIVE.value,
                Account.is_deleted == False
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting active accounts: {str(e)}")
            raise DatabaseException("Failed to get accounts", e)
    
    def search_accounts(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Account]:
        """
        Search accounts by account number or customer name.
        
        Args:
            search_term: Search term
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[Account]: List of matching accounts
        """
        try:
            search_pattern = f"%{search_term}%"
            return self.db.query(Account).filter(
                or_(
                    Account.account_number.ilike(search_pattern),
                    Account.customer_name.ilike(search_pattern),
                    Account.mmi_id.ilike(search_pattern)
                ),
                Account.is_deleted == False
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error searching accounts: {str(e)}")
            raise DatabaseException("Failed to search accounts", e)
    
    def create_account(
        self,
        account_number: str,
        customer_name: str,
        mmi_id: str,
        account_type: str,
        currency: str = "USD",
        created_by: int = None,
        **kwargs
    ) -> Account:
        """
        Create a new account with duplicate check.
        
        Args:
            account_number: Account number (must be unique)
            customer_name: Customer name
            mmi_id: MMI ID
            account_type: Account type
            currency: Currency code
            created_by: User ID who created the account
            **kwargs: Additional attributes
            
        Returns:
            Account: Created account object
            
        Raises:
            DuplicateAccountException: If account number already exists
            DatabaseException: If creation fails
        """
        # Check for duplicate
        if self.get_by_account_number(account_number):
            raise DuplicateAccountException(account_number)
        
        try:
            account = Account(
                account_number=account_number,
                customer_name=customer_name,
                mmi_id=mmi_id,
                account_type=account_type,
                currency=currency,
                created_by=created_by,
                **kwargs
            )
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            logger.info(f"Account created: {account_number}")
            return account
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating account: {str(e)}")
            raise DatabaseException("Failed to create account", e)
    
    def update_account(
        self,
        account_id: int,
        customer_name: Optional[str] = None,
        mmi_id: Optional[str] = None,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        current_balance: Optional[float] = None,
        pending_hold_amount: Optional[float] = None,
        modified_by: Optional[int] = None,
        **kwargs
    ) -> Optional[Account]:
        """
        Update an account.
        
        Args:
            account_id: Account ID
            customer_name: New customer name
            mmi_id: New MMI ID
            account_type: New account type
            status: New status
            current_balance: New balance
            pending_hold_amount: New pending hold amount
            modified_by: User ID who modified
            **kwargs: Additional attributes
            
        Returns:
            Account: Updated account or None if not found
        """
        try:
            account = self.get_by_id(account_id)
            if not account:
                raise AccountNotFoundException(account_id=account_id)
            
            if customer_name is not None:
                account.customer_name = customer_name
            if mmi_id is not None:
                account.mmi_id = mmi_id
            if account_type is not None:
                account.account_type = account_type
            if status is not None:
                account.status = status
            if current_balance is not None:
                account.current_balance = current_balance
            if pending_hold_amount is not None:
                account.pending_hold_amount = pending_hold_amount
            
            account.modified_by = modified_by
            account.modified_at = datetime.utcnow()
            
            for key, value in kwargs.items():
                if hasattr(account, key):
                    setattr(account, key, value)
            
            self.db.commit()
            self.db.refresh(account)
            logger.info(f"Account updated: {account.account_number}")
            return account
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating account: {str(e)}")
            raise DatabaseException("Failed to update account", e)
    
    def deactivate_account(self, account_id: int, modified_by: int) -> Optional[Account]:
        """
        Deactivate an account.
        
        Args:
            account_id: Account ID
            modified_by: User ID who deactivated
            
        Returns:
            Account: Deactivated account or None if not found
        """
        return self.update_account(
            account_id,
            status=AccountStatusEnum.INACTIVE.value,
            modified_by=modified_by
        )
    
    def suspend_account(self, account_id: int, modified_by: int) -> Optional[Account]:
        """
        Suspend an account.
        
        Args:
            account_id: Account ID
            modified_by: User ID who suspended
            
        Returns:
            Account: Suspended account or None if not found
        """
        return self.update_account(
            account_id,
            status=AccountStatusEnum.SUSPENDED.value,
            modified_by=modified_by
        )
    
    def get_accounts_with_pending_holds(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Account]:
        """
        Get accounts with pending holds.
        
        Args:
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[Account]: Accounts with pending holds
        """
        try:
            return self.db.query(Account).filter(
                Account.pending_hold_amount > 0,
                Account.is_deleted == False
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting accounts with pending holds: {str(e)}")
            raise DatabaseException("Failed to get accounts", e)
    
    def get_account_statistics(self) -> Dict[str, Any]:
        """
        Get account statistics.
        
        Returns:
            Dict: Statistics including counts, totals, averages
        """
        try:
            total_accounts = self.db.query(Account).filter(
                Account.is_deleted == False
            ).count()
            
            active_accounts = self.db.query(Account).filter(
                Account.status == AccountStatusEnum.ACTIVE.value,
                Account.is_deleted == False
            ).count()
            
            total_balance = self.db.query(Account).filter(
                Account.is_deleted == False
            ).with_entities(
                self.db.func.sum(Account.current_balance)
            ).scalar() or 0
            
            total_pending_holds = self.db.query(Account).filter(
                Account.is_deleted == False
            ).with_entities(
                self.db.func.sum(Account.pending_hold_amount)
            ).scalar() or 0
            
            return {
                "total_accounts": total_accounts,
                "active_accounts": active_accounts,
                "inactive_accounts": total_accounts - active_accounts,
                "total_balance": float(total_balance),
                "total_pending_holds": float(total_pending_holds),
                "available_balance": float(total_balance - total_pending_holds)
            }
        except Exception as e:
            logger.error(f"Error getting account statistics: {str(e)}")
            raise DatabaseException("Failed to get statistics", e)
