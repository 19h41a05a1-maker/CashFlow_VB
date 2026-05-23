"""
Transaction repository for transaction data access.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging

from app.database.models import Transaction, TransactionStatusEnum, TransactionTypeEnum
from app.repositories.base_repository import BaseRepository
from app.exceptions.base_exception import DatabaseException

logger = logging.getLogger(__name__)


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for transaction operations."""
    
    def __init__(self, db: Session):
        """Initialize transaction repository."""
        super().__init__(db, Transaction)
    
    def get_by_transaction_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get transaction by transaction ID.
        
        Args:
            transaction_id: Transaction ID to search
            
        Returns:
            Transaction: Transaction object or None if not found
        """
        try:
            return self.db.query(Transaction).filter(
                Transaction.transaction_id == transaction_id,
                Transaction.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"Error getting transaction by ID: {str(e)}")
            raise DatabaseException("Failed to get transaction", e)
    
    def get_account_transactions(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        order_by_desc: bool = True
    ) -> List[Transaction]:
        """
        Get all transactions for an account.
        
        Args:
            account_id: Account ID
            skip: Offset for pagination
            limit: Limit for pagination
            order_by_desc: Sort by date descending if True
            
        Returns:
            List[Transaction]: List of transactions
        """
        try:
            query = self.db.query(Transaction).filter(
                Transaction.account_id == account_id,
                Transaction.is_deleted == False
            )
            
            if order_by_desc:
                query = query.order_by(Transaction.transaction_date.desc())
            else:
                query = query.order_by(Transaction.transaction_date.asc())
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting account transactions: {str(e)}")
            raise DatabaseException("Failed to get transactions", e)
    
    def get_account_credits(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """
        Get credit transactions for an account.
        
        Args:
            account_id: Account ID
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[Transaction]: List of credit transactions
        """
        try:
            credit_types = [
                TransactionTypeEnum.ACH_CREDIT.value,
                TransactionTypeEnum.CHEQUE_CREDIT.value,
                TransactionTypeEnum.WIRE_CREDIT.value,
                TransactionTypeEnum.OTHER_CREDIT.value,
            ]
            
            return self.db.query(Transaction).filter(
                Transaction.account_id == account_id,
                Transaction.transaction_type.in_(credit_types),
                Transaction.is_deleted == False
            ).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting account credits: {str(e)}")
            raise DatabaseException("Failed to get credits", e)
    
    def get_account_debits(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """
        Get debit transactions for an account.
        
        Args:
            account_id: Account ID
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[Transaction]: List of debit transactions
        """
        try:
            debit_types = [
                TransactionTypeEnum.ACH_DEBIT.value,
                TransactionTypeEnum.WIRE_TRANSFER.value,
                TransactionTypeEnum.CHEQUE_PAYMENT.value,
                TransactionTypeEnum.MANUAL_DEBIT.value,
            ]
            
            return self.db.query(Transaction).filter(
                Transaction.account_id == account_id,
                Transaction.transaction_type.in_(debit_types),
                Transaction.is_deleted == False
            ).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting account debits: {str(e)}")
            raise DatabaseException("Failed to get debits", e)
    
    def get_transactions_by_date_range(
        self,
        account_id: int,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """
        Get transactions within a date range.
        
        Args:
            account_id: Account ID
            start_date: Start date
            end_date: End date
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[Transaction]: List of transactions in date range
        """
        try:
            return self.db.query(Transaction).filter(
                Transaction.account_id == account_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
                Transaction.is_deleted == False
            ).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting transactions by date range: {str(e)}")
            raise DatabaseException("Failed to get transactions", e)
    
    def get_recent_credits(
        self,
        account_id: int,
        days: int = 5
    ) -> List[Transaction]:
        """
        Get credits received in the last N days.
        
        Args:
            account_id: Account ID
            days: Number of days to look back
            
        Returns:
            List[Transaction]: List of recent credits
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            credit_types = [
                TransactionTypeEnum.ACH_CREDIT.value,
                TransactionTypeEnum.CHEQUE_CREDIT.value,
                TransactionTypeEnum.WIRE_CREDIT.value,
                TransactionTypeEnum.OTHER_CREDIT.value,
            ]
            
            return self.db.query(Transaction).filter(
                Transaction.account_id == account_id,
                Transaction.transaction_type.in_(credit_types),
                Transaction.transaction_date >= cutoff_date,
                Transaction.is_deleted == False
            ).order_by(Transaction.transaction_date.desc()).all()
        except Exception as e:
            logger.error(f"Error getting recent credits: {str(e)}")
            raise DatabaseException("Failed to get credits", e)
    
    def get_account_totals(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get total credits and debits for an account.
        
        Args:
            account_id: Account ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dict: Total credits and debits
        """
        try:
            query = self.db.query(Transaction).filter(
                Transaction.account_id == account_id,
                Transaction.is_deleted == False
            )
            
            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)
            
            transactions = query.all()
            
            credit_types = [
                TransactionTypeEnum.ACH_CREDIT.value,
                TransactionTypeEnum.CHEQUE_CREDIT.value,
                TransactionTypeEnum.WIRE_CREDIT.value,
                TransactionTypeEnum.OTHER_CREDIT.value,
            ]
            
            total_credits = sum(
                t.amount for t in transactions if t.transaction_type in credit_types
            )
            total_debits = sum(
                t.amount for t in transactions if t.transaction_type not in credit_types
            )
            
            return {
                "total_credits": total_credits,
                "total_debits": total_debits,
                "net": total_credits - total_debits
            }
        except Exception as e:
            logger.error(f"Error getting account totals: {str(e)}")
            raise DatabaseException("Failed to get account totals", e)
    
    def create_transaction(
        self,
        transaction_id: str,
        account_id: int,
        transaction_type: str,
        amount: float,
        transaction_date: datetime,
        status: str,
        created_by: int,
        reference_number: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            transaction_id: Unique transaction ID
            account_id: Account ID
            transaction_type: Type of transaction
            amount: Transaction amount
            transaction_date: Date of transaction
            status: Transaction status
            created_by: User ID who created
            reference_number: Optional reference number
            description: Optional description
            **kwargs: Additional attributes
            
        Returns:
            Transaction: Created transaction
        """
        try:
            transaction = Transaction(
                transaction_id=transaction_id,
                account_id=account_id,
                transaction_type=transaction_type,
                amount=amount,
                transaction_date=transaction_date,
                status=status,
                reference_number=reference_number,
                description=description,
                created_by=created_by,
                **kwargs
            )
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            logger.info(f"Transaction created: {transaction_id}")
            return transaction
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating transaction: {str(e)}")
            raise DatabaseException("Failed to create transaction", e)
