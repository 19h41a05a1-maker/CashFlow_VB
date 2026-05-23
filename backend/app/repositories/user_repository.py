"""
User repository for user data access operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
import logging

from app.repositories.base_repository import BaseRepository
from app.database.models import User
from app.exceptions.base_exception import (
    UserNotFoundException,
    DuplicateAccountException,
    DatabaseException
)

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for user data access."""
    
    def __init__(self, db: Session):
        """
        Initialize user repository.
        
        Args:
            db: SQLAlchemy session
        """
        super().__init__(db, User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User: User object or None
        """
        try:
            user = self.db.query(User).filter(
                User.username == username
            ).first()
            
            if user:
                logger.debug(f"User retrieved by username: {username}")
            else:
                logger.debug(f"User not found by username: {username}")
            
            return user
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email address
            
        Returns:
            User: User object or None
        """
        try:
            user = self.db.query(User).filter(
                User.email == email
            ).first()
            
            if user:
                logger.debug(f"User retrieved by email: {email}")
            else:
                logger.debug(f"User not found by email: {email}")
            
            return user
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        created_by: int = 0
    ) -> User:
        """
        Create new user.
        
        Args:
            username: Username
            email: Email address
            password_hash: Hashed password
            created_by: User ID creating the user
            
        Returns:
            User: Created user
            
        Raises:
            DuplicateAccountException: If username or email already exists
        """
        try:
            # Check if username exists
            existing_user = self.get_by_username(username)
            if existing_user:
                logger.warning(f"Duplicate username attempted: {username}")
                raise DuplicateAccountException(username=username)
            
            # Check if email exists
            existing_email = self.get_by_email(email)
            if existing_email:
                logger.warning(f"Duplicate email attempted: {email}")
                raise DuplicateAccountException(email=email)
            
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                created_by=created_by
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User created: {username}")
            return user
        except DuplicateAccountException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def update_user(
        self,
        user_id: int,
        **kwargs
    ) -> User:
        """
        Update user.
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            User: Updated user
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundException(user_id=user_id)
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User updated: {user_id}")
            return user
        except UserNotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Get active users.
        
        Args:
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[User]: List of active users
        """
        try:
            users = self.db.query(User).filter(
                User.status == "ACTIVE"
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(users)} active users")
            return users
        except Exception as e:
            logger.error(f"Error getting active users: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def lock_account(self, user_id: int) -> User:
        """
        Lock user account after failed login attempts.
        
        Args:
            user_id: User ID
            
        Returns:
            User: Updated user
        """
        try:
            from datetime import datetime, timedelta
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundException(user_id=user_id)
            
            user.status = "LOCKED"
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.warning(f"User account locked: {user_id}")
            return user
        except UserNotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error locking account: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def unlock_account(self, user_id: int) -> User:
        """
        Unlock user account.
        
        Args:
            user_id: User ID
            
        Returns:
            User: Updated user
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundException(user_id=user_id)
            
            user.status = "ACTIVE"
            user.locked_until = None
            user.failed_login_attempts = 0
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User account unlocked: {user_id}")
            return user
        except UserNotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error unlocking account: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def reset_failed_login_attempts(self, user_id: int) -> User:
        """
        Reset failed login attempts counter.
        
        Args:
            user_id: User ID
            
        Returns:
            User: Updated user
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundException(user_id=user_id)
            
            user.failed_login_attempts = 0
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.debug(f"Failed login attempts reset: {user_id}")
            return user
        except UserNotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting failed login attempts: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def increment_failed_login_attempts(self, user_id: int) -> User:
        """
        Increment failed login attempts counter.
        
        Args:
            user_id: User ID
            
        Returns:
            User: Updated user
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundException(user_id=user_id)
            
            user.failed_login_attempts += 1
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.debug(f"Failed login attempts incremented: {user_id}")
            return user
        except UserNotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error incrementing failed login attempts: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Search users by username or email.
        
        Args:
            search_term: Search term
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[User]: List of matching users
        """
        try:
            users = self.db.query(User).filter(
                (User.username.ilike(f"%{search_term}%")) |
                (User.email.ilike(f"%{search_term}%"))
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(users)} users matching: {search_term}")
            return users
        except Exception as e:
            logger.error(f"Error searching users: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_user_statistics(self) -> dict:
        """
        Get user statistics.
        
        Returns:
            dict: Statistics
        """
        try:
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.status == "ACTIVE").count()
            locked_users = self.db.query(User).filter(User.status == "LOCKED").count()
            suspended_users = self.db.query(User).filter(User.status == "SUSPENDED").count()
            
            stats = {
                "total_users": total_users,
                "active_users": active_users,
                "locked_users": locked_users,
                "suspended_users": suspended_users,
                "inactive_users": total_users - active_users
            }
            
            logger.debug("User statistics retrieved")
            return stats
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
