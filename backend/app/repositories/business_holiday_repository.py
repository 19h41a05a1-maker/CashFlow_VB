"""
Business holiday repository for holiday management data access operations.
"""

from typing import Optional, List
from datetime import date, datetime
from sqlalchemy.orm import Session
import logging

from app.repositories.base_repository import BaseRepository
from app.database.models import BusinessHoliday
from app.exceptions.base_exception import DatabaseException

logger = logging.getLogger(__name__)


class BusinessHolidayRepository(BaseRepository[BusinessHoliday]):
    """Repository for business holiday data access."""
    
    def __init__(self, db: Session):
        """
        Initialize business holiday repository.
        
        Args:
            db: SQLAlchemy session
        """
        super().__init__(db, BusinessHoliday)
    
    def get_by_date(self, holiday_date: date) -> Optional[BusinessHoliday]:
        """
        Get holiday by date.
        
        Args:
            holiday_date: Date to check
            
        Returns:
            BusinessHoliday: Holiday object or None
        """
        try:
            holiday = self.db.query(BusinessHoliday).filter(
                BusinessHoliday.holiday_date == holiday_date
            ).first()
            
            if holiday:
                logger.debug(f"Holiday retrieved: {holiday_date}")
            else:
                logger.debug(f"No holiday found for: {holiday_date}")
            
            return holiday
        except Exception as e:
            logger.error(f"Error getting holiday by date: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_holidays_in_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[BusinessHoliday]:
        """
        Get holidays within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List[BusinessHoliday]: List of holidays in range
        """
        try:
            holidays = self.db.query(BusinessHoliday).filter(
                BusinessHoliday.holiday_date >= start_date,
                BusinessHoliday.holiday_date <= end_date
            ).order_by(BusinessHoliday.holiday_date).all()
            
            logger.debug(
                f"Retrieved {len(holidays)} holidays between {start_date} and {end_date}"
            )
            return holidays
        except Exception as e:
            logger.error(f"Error getting holidays in range: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_active_holidays(self) -> List[BusinessHoliday]:
        """
        Get all active holidays.
        
        Returns:
            List[BusinessHoliday]: List of active holidays
        """
        try:
            holidays = self.db.query(BusinessHoliday).filter(
                BusinessHoliday.is_active == True
            ).order_by(BusinessHoliday.holiday_date).all()
            
            logger.debug(f"Retrieved {len(holidays)} active holidays")
            return holidays
        except Exception as e:
            logger.error(f"Error getting active holidays: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def add_holiday(
        self,
        holiday_date: date,
        holiday_name: str,
        is_recurring: bool = False,
        created_by: int = 0
    ) -> BusinessHoliday:
        """
        Add a new holiday.
        
        Args:
            holiday_date: Holiday date
            holiday_name: Name of holiday
            is_recurring: Whether holiday recurs annually
            created_by: User ID creating holiday
            
        Returns:
            BusinessHoliday: Created holiday
        """
        try:
            # Check if holiday already exists
            existing = self.get_by_date(holiday_date)
            if existing:
                logger.warning(f"Holiday already exists for {holiday_date}")
                return existing
            
            holiday = BusinessHoliday(
                holiday_date=holiday_date,
                holiday_name=holiday_name,
                is_active=True,
                is_recurring=is_recurring,
                created_by=created_by
            )
            
            self.db.add(holiday)
            self.db.commit()
            self.db.refresh(holiday)
            
            logger.info(f"Holiday added: {holiday_date} - {holiday_name}")
            return holiday
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding holiday: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def remove_holiday(self, holiday_date: date) -> bool:
        """
        Remove a holiday.
        
        Args:
            holiday_date: Holiday date to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        try:
            holiday = self.get_by_date(holiday_date)
            if not holiday:
                logger.warning(f"Holiday not found for removal: {holiday_date}")
                return False
            
            self.db.delete(holiday)
            self.db.commit()
            
            logger.info(f"Holiday removed: {holiday_date}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing holiday: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def deactivate_holiday(self, holiday_date: date) -> Optional[BusinessHoliday]:
        """
        Deactivate a holiday without removing it.
        
        Args:
            holiday_date: Holiday date
            
        Returns:
            BusinessHoliday: Updated holiday or None
        """
        try:
            holiday = self.get_by_date(holiday_date)
            if not holiday:
                logger.warning(f"Holiday not found for deactivation: {holiday_date}")
                return None
            
            holiday.is_active = False
            
            self.db.commit()
            self.db.refresh(holiday)
            
            logger.info(f"Holiday deactivated: {holiday_date}")
            return holiday
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating holiday: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def reactivate_holiday(self, holiday_date: date) -> Optional[BusinessHoliday]:
        """
        Reactivate a holiday.
        
        Args:
            holiday_date: Holiday date
            
        Returns:
            BusinessHoliday: Updated holiday or None
        """
        try:
            holiday = self.get_by_date(holiday_date)
            if not holiday:
                logger.warning(f"Holiday not found for reactivation: {holiday_date}")
                return None
            
            holiday.is_active = True
            
            self.db.commit()
            self.db.refresh(holiday)
            
            logger.info(f"Holiday reactivated: {holiday_date}")
            return holiday
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error reactivating holiday: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_upcoming_holidays(self, days_ahead: int = 30) -> List[BusinessHoliday]:
        """
        Get upcoming holidays.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List[BusinessHoliday]: List of upcoming holidays
        """
        try:
            from datetime import datetime, timedelta
            
            today = datetime.utcnow().date()
            future_date = today + timedelta(days=days_ahead)
            
            holidays = self.db.query(BusinessHoliday).filter(
                BusinessHoliday.holiday_date >= today,
                BusinessHoliday.holiday_date <= future_date,
                BusinessHoliday.is_active == True
            ).order_by(BusinessHoliday.holiday_date).all()
            
            logger.debug(f"Retrieved {len(holidays)} upcoming holidays")
            return holidays
        except Exception as e:
            logger.error(f"Error getting upcoming holidays: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_holidays_by_year(self, year: int) -> List[BusinessHoliday]:
        """
        Get all holidays for a given year.
        
        Args:
            year: Year
            
        Returns:
            List[BusinessHoliday]: List of holidays
        """
        try:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
            holidays = self.get_holidays_in_range(start_date, end_date)
            logger.debug(f"Retrieved {len(holidays)} holidays for year {year}")
            return holidays
        except Exception as e:
            logger.error(f"Error getting holidays by year: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def bulk_add_holidays(
        self,
        holidays_data: List[dict],
        created_by: int = 0
    ) -> List[BusinessHoliday]:
        """
        Bulk add holidays.
        
        Args:
            holidays_data: List of dicts with holiday_date, holiday_name
            created_by: User ID creating holidays
            
        Returns:
            List[BusinessHoliday]: Created holidays
        """
        try:
            created_holidays = []
            
            for holiday_data in holidays_data:
                holiday = self.add_holiday(
                    holiday_date=holiday_data["holiday_date"],
                    holiday_name=holiday_data["holiday_name"],
                    is_recurring=holiday_data.get("is_recurring", False),
                    created_by=created_by
                )
                created_holidays.append(holiday)
            
            logger.info(f"Bulk added {len(created_holidays)} holidays")
            return created_holidays
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk adding holidays: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
    
    def get_holiday_statistics(self) -> dict:
        """
        Get holiday statistics.
        
        Returns:
            dict: Statistics
        """
        try:
            total_holidays = self.db.query(BusinessHoliday).count()
            active_holidays = self.db.query(BusinessHoliday).filter(
                BusinessHoliday.is_active == True
            ).count()
            recurring_holidays = self.db.query(BusinessHoliday).filter(
                BusinessHoliday.is_recurring == True
            ).count()
            
            stats = {
                "total_holidays": total_holidays,
                "active_holidays": active_holidays,
                "inactive_holidays": total_holidays - active_holidays,
                "recurring_holidays": recurring_holidays,
                "one_time_holidays": total_holidays - recurring_holidays
            }
            
            logger.debug("Holiday statistics retrieved")
            return stats
        except Exception as e:
            logger.error(f"Error getting holiday statistics: {str(e)}")
            raise DatabaseException(str(e), original_error=e)
