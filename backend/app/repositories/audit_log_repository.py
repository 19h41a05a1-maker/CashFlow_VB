"""
Audit log repository for audit logging data access operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import logging
import json

from app.repositories.base_repository import BaseRepository
from app.database.models import AuditLog
from app.exceptions.base_exception import DatabaseException

logger = logging.getLogger(__name__)


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for audit log data access."""
    
    def __init__(self, db: Session):
        """
        Initialize audit log repository.
        
        Args:
            db: SQLAlchemy session
        """
        super().__init__(db, AuditLog)
    
    def log_action(
        self,
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: int,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[str] = None
    ) -> AuditLog:
        """
        Log an action to the audit log.
        
        Args:
            user_id: User ID performing the action
            action: Action name (CREATE, UPDATE, DELETE, LOGIN, etc.)
            entity_type: Type of entity (Account, Transaction, User, etc.)
            entity_id: ID of the entity
            old_values: Previous values (for updates)
            new_values: New values (for updates)
            ip_address: IP address of request
            status: Action status (SUCCESS, FAILURE)
            details: Additional details
            
        Returns:
            AuditLog: Created audit log record
        """
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
                ip_address=ip_address,
                status=status,
                details=details,
                created_at=datetime.utcnow()
            )
            
            self.db.add(audit_log)
            self.db.commit()
            self.db.refresh(audit_log)
            
            logger.info(
                f"Audit log created: user={user_id}, action={action}, "
                f"entity={entity_type}:{entity_id}, status={status}"
            )
            return audit_log
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging action: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        action: Optional[str] = None
    ) -> List[AuditLog]:
        """
        Get audit logs for a user.
        
        Args:
            user_id: User ID
            skip: Offset for pagination
            limit: Limit for pagination
            action: Optional action filter
            
        Returns:
            List[AuditLog]: List of audit logs
        """
        try:
            query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
            
            if action:
                query = query.filter(AuditLog.action == action)
            
            audit_logs = query.order_by(
                AuditLog.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(audit_logs)} audit logs for user {user_id}")
            return audit_logs
        except Exception as e:
            logger.error(f"Error getting audit logs by user: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_by_entity(
        self,
        entity_type: str,
        entity_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs for an entity.
        
        Args:
            entity_type: Type of entity (Account, Transaction, etc.)
            entity_id: ID of entity
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List[AuditLog]: List of audit logs
        """
        try:
            audit_logs = self.db.query(AuditLog).filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id
            ).order_by(
                AuditLog.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            logger.debug(
                f"Retrieved {len(audit_logs)} audit logs for {entity_type}:{entity_id}"
            )
            return audit_logs
        except Exception as e:
            logger.error(f"Error getting audit logs by entity: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_by_action(
        self,
        action: str,
        skip: int = 0,
        limit: int = 100,
        entity_type: Optional[str] = None
    ) -> List[AuditLog]:
        """
        Get audit logs by action type.
        
        Args:
            action: Action name (CREATE, UPDATE, DELETE, etc.)
            skip: Offset for pagination
            limit: Limit for pagination
            entity_type: Optional entity type filter
            
        Returns:
            List[AuditLog]: List of audit logs
        """
        try:
            query = self.db.query(AuditLog).filter(AuditLog.action == action)
            
            if entity_type:
                query = query.filter(AuditLog.entity_type == entity_type)
            
            audit_logs = query.order_by(
                AuditLog.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(audit_logs)} audit logs for action {action}")
            return audit_logs
        except Exception as e:
            logger.error(f"Error getting audit logs by action: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        action: Optional[str] = None
    ) -> List[AuditLog]:
        """
        Get audit logs within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            skip: Offset for pagination
            limit: Limit for pagination
            user_id: Optional user filter
            entity_type: Optional entity type filter
            action: Optional action filter
            
        Returns:
            List[AuditLog]: List of audit logs
        """
        try:
            query = self.db.query(AuditLog).filter(
                AuditLog.created_at >= start_date,
                AuditLog.created_at <= end_date
            )
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if entity_type:
                query = query.filter(AuditLog.entity_type == entity_type)
            
            if action:
                query = query.filter(AuditLog.action == action)
            
            audit_logs = query.order_by(
                AuditLog.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            logger.debug(
                f"Retrieved {len(audit_logs)} audit logs between {start_date} and {end_date}"
            )
            return audit_logs
        except Exception as e:
            logger.error(f"Error getting audit logs by date range: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_failed_actions(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None
    ) -> List[AuditLog]:
        """
        Get failed audit actions.
        
        Args:
            skip: Offset for pagination
            limit: Limit for pagination
            user_id: Optional user filter
            
        Returns:
            List[AuditLog]: List of failed audit logs
        """
        try:
            query = self.db.query(AuditLog).filter(AuditLog.status == "FAILURE")
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            audit_logs = query.order_by(
                AuditLog.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(audit_logs)} failed audit actions")
            return audit_logs
        except Exception as e:
            logger.error(f"Error getting failed audit actions: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_user_activity_summary(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get user activity summary.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Dict: Activity summary
        """
        try:
            audit_logs = self.db.query(AuditLog).filter(
                AuditLog.user_id == user_id,
                AuditLog.created_at >= start_date,
                AuditLog.created_at <= end_date
            ).all()
            
            total_actions = len(audit_logs)
            successful_actions = len([al for al in audit_logs if al.status == "SUCCESS"])
            failed_actions = len([al for al in audit_logs if al.status == "FAILURE"])
            
            # Group by action type
            action_counts = {}
            for al in audit_logs:
                action_counts[al.action] = action_counts.get(al.action, 0) + 1
            
            # Group by entity type
            entity_counts = {}
            for al in audit_logs:
                entity_counts[al.entity_type] = entity_counts.get(al.entity_type, 0) + 1
            
            summary = {
                "user_id": user_id,
                "total_actions": total_actions,
                "successful_actions": successful_actions,
                "failed_actions": failed_actions,
                "success_rate": (successful_actions / total_actions * 100) if total_actions > 0 else 0,
                "action_breakdown": action_counts,
                "entity_breakdown": entity_counts,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
            logger.debug(f"User activity summary retrieved for user {user_id}")
            return summary
        except Exception as e:
            logger.error(f"Error getting user activity summary: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_audit_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get overall audit statistics.
        
        Args:
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Dict: Audit statistics
        """
        try:
            query = self.db.query(AuditLog)
            
            if start_date:
                query = query.filter(AuditLog.created_at >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.created_at <= end_date)
            
            audit_logs = query.all()
            
            total_actions = len(audit_logs)
            successful_actions = len([al for al in audit_logs if al.status == "SUCCESS"])
            failed_actions = len([al for al in audit_logs if al.status == "FAILURE"])
            
            # Group by action
            action_counts = {}
            for al in audit_logs:
                action_counts[al.action] = action_counts.get(al.action, 0) + 1
            
            # Group by entity
            entity_counts = {}
            for al in audit_logs:
                entity_counts[al.entity_type] = entity_counts.get(al.entity_type, 0) + 1
            
            # Unique users
            unique_users = len(set(al.user_id for al in audit_logs))
            
            stats = {
                "total_actions": total_actions,
                "successful_actions": successful_actions,
                "failed_actions": failed_actions,
                "success_rate": (successful_actions / total_actions * 100) if total_actions > 0 else 0,
                "unique_users": unique_users,
                "top_actions": sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                "top_entities": sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            }
            
            logger.debug("Audit statistics retrieved")
            return stats
        except Exception as e:
            logger.error(f"Error getting audit statistics: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def cleanup_old_logs(self, days: int = 90) -> int:
        """
        Delete audit logs older than N days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            int: Number of records deleted
        """
        try:
            cutoff_date = datetime.utcnow().timestamp() - (days * 86400)
            
            deleted_count = self.db.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Cleaned up {deleted_count} audit logs older than {days} days")
            return deleted_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cleaning up old audit logs: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
