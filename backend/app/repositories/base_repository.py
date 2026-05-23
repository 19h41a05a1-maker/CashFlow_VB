"""
Base repository with common CRUD operations.
"""

from typing import TypeVar, Generic, List, Optional, Type, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.exceptions.base_exception import DatabaseException

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Base repository class providing common CRUD operations.
    
    Type Parameters:
        T: The model class this repository manages
    """
    
    def __init__(self, db: Session, model: Type[T]):
        """
        Initialize base repository.
        
        Args:
            db: SQLAlchemy session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model
    
    def create(self, **kwargs) -> T:
        """
        Create a new record.
        
        Args:
            **kwargs: Model attributes
            
        Returns:
            T: Created model instance
            
        Raises:
            DatabaseException: If creation fails
        """
        try:
            db_obj = self.model(**kwargs)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to create {self.model.__name__}", e)
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Get record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            T: Model instance or None if not found
        """
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by ID: {str(e)}")
            raise DatabaseException(f"Failed to get {self.model.__name__}", e)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get all records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List[T]: List of model instances
        """
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to get {self.model.__name__} records", e)
    
    def get_filtered(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[T]:
        """
        Get records with filtering.
        
        Args:
            filters: Dictionary of column-value filters
            skip: Number of records to skip
            limit: Number of records to return
            order_by: Field name to order by
            
        Returns:
            List[T]: Filtered list of model instances
        """
        try:
            query = self.db.query(self.model)
            
            # Apply filters
            for column, value in filters.items():
                if hasattr(self.model, column):
                    query = query.filter(getattr(self.model, column) == value)
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error filtering {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to filter {self.model.__name__}", e)
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """
        Update a record.
        
        Args:
            id: Record ID
            **kwargs: Attributes to update
            
        Returns:
            T: Updated model instance or None if not found
            
        Raises:
            DatabaseException: If update fails
        """
        try:
            db_obj = self.get_by_id(id)
            if not db_obj:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to update {self.model.__name__}", e)
    
    def delete(self, id: int) -> bool:
        """
        Delete a record (hard delete).
        
        Args:
            id: Record ID
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            DatabaseException: If deletion fails
        """
        try:
            db_obj = self.get_by_id(id)
            if not db_obj:
                return False
            
            self.db.delete(db_obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to delete {self.model.__name__}", e)
    
    def soft_delete(self, id: int) -> Optional[T]:
        """
        Soft delete a record (mark as deleted).
        
        Args:
            id: Record ID
            
        Returns:
            T: Soft-deleted model instance or None if not found
            
        Raises:
            DatabaseException: If deletion fails
        """
        from datetime import datetime
        try:
            db_obj = self.get_by_id(id)
            if not db_obj:
                return None
            
            if hasattr(db_obj, 'is_deleted'):
                db_obj.is_deleted = True
            if hasattr(db_obj, 'deleted_at'):
                db_obj.deleted_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error soft deleting {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to soft delete {self.model.__name__}", e)
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records.
        
        Args:
            filters: Optional dictionary of filters
            
        Returns:
            int: Record count
        """
        try:
            query = self.db.query(self.model)
            
            if filters:
                for column, value in filters.items():
                    if hasattr(self.model, column):
                        query = query.filter(getattr(self.model, column) == value)
            
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to count {self.model.__name__}", e)
    
    def exists(self, **filters) -> bool:
        """
        Check if record exists.
        
        Args:
            **filters: Column-value filters
            
        Returns:
            bool: True if record exists
        """
        try:
            query = self.db.query(self.model)
            
            for column, value in filters.items():
                if hasattr(self.model, column):
                    query = query.filter(getattr(self.model, column) == value)
            
            return query.first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__}: {str(e)}")
            return False
    
    def bulk_create(self, objects: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple records in bulk.
        
        Args:
            objects: List of dictionaries with model attributes
            
        Returns:
            List[T]: List of created model instances
            
        Raises:
            DatabaseException: If bulk creation fails
        """
        try:
            db_objects = [self.model(**obj) for obj in objects]
            self.db.add_all(db_objects)
            self.db.commit()
            
            # Refresh to get IDs
            for obj in db_objects:
                self.db.refresh(obj)
            
            return db_objects
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error bulk creating {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to bulk create {self.model.__name__}", e)
    
    def bulk_update(self, updates: Dict[int, Dict[str, Any]]) -> List[T]:
        """
        Update multiple records.
        
        Args:
            updates: Dictionary mapping record ID to update attributes
            
        Returns:
            List[T]: List of updated model instances
            
        Raises:
            DatabaseException: If bulk update fails
        """
        try:
            updated_objects = []
            
            for id, update_dict in updates.items():
                obj = self.update(id, **update_dict)
                if obj:
                    updated_objects.append(obj)
            
            return updated_objects
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error bulk updating {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to bulk update {self.model.__name__}", e)
    
    def execute_raw(self, query: str) -> Any:
        """
        Execute raw SQL query (use with caution).
        
        Args:
            query: Raw SQL query (must be parameterized)
            
        Returns:
            Any: Query result
            
        Raises:
            DatabaseException: If query fails
        """
        try:
            return self.db.execute(query).fetchall()
        except SQLAlchemyError as e:
            logger.error(f"Error executing raw query: {str(e)}")
            raise DatabaseException("Failed to execute raw query", e)
