"""
Business day calculation utilities for 5-day hold computation.
"""

from datetime import datetime, timedelta, date
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class BusinessDayCalculator:
    """Calculator for business day operations."""
    
    # US Federal holidays - can be overridden via configuration
    DEFAULT_HOLIDAYS = [
        "2026-01-01",  # New Year's Day
        "2026-01-19",  # MLK Day
        "2026-02-16",  # Presidents Day
        "2026-03-27",  # Good Friday
        "2026-05-25",  # Memorial Day
        "2026-06-19",  # Juneteenth
        "2026-07-04",  # Independence Day
        "2026-09-07",  # Labor Day
        "2026-10-12",  # Columbus Day
        "2026-11-11",  # Veterans Day
        "2026-11-26",  # Thanksgiving
        "2026-12-25",  # Christmas
    ]
    
    def __init__(self, holidays: Optional[List[str]] = None):
        """
        Initialize business day calculator.
        
        Args:
            holidays: List of holiday dates in YYYY-MM-DD format
        """
        self.holidays = set()
        self._load_holidays(holidays or self.DEFAULT_HOLIDAYS)
    
    def _load_holidays(self, holidays: List[str]) -> None:
        """
        Load holidays from string list.
        
        Args:
            holidays: List of holiday dates in YYYY-MM-DD format
        """
        for holiday_str in holidays:
            try:
                holiday_date = datetime.strptime(holiday_str, "%Y-%m-%d").date()
                self.holidays.add(holiday_date)
            except ValueError as e:
                logger.warning(f"Invalid holiday format {holiday_str}: {str(e)}")
    
    def is_business_day(self, check_date: date) -> bool:
        """
        Check if a date is a business day (not weekend or holiday).
        
        Args:
            check_date: Date to check
            
        Returns:
            bool: True if business day, False otherwise
        """
        # Check if weekend (Monday=0, Sunday=6)
        if check_date.weekday() >= 5:
            return False
        
        # Check if holiday
        if check_date in self.holidays:
            return False
        
        return True
    
    def calculate_hold_expiry_date(self, credit_date: datetime, hold_days: int = 5) -> datetime:
        """
        Calculate the hold expiry date from credit date.
        
        Args:
            credit_date: Date when credit was received
            hold_days: Number of business days to hold (default 5)
            
        Returns:
            datetime: Hold expiry date at 23:59:59
            
        Example:
            Credit received: Friday, May 23
            Hold Period: 5 business days (Mon-Fri)
            Hold Expiry: Friday, May 30 at 23:59:59
        """
        current_date = credit_date.date()
        business_days_counted = 0
        
        # Start counting from the next day after credit
        current_date += timedelta(days=1)
        
        while business_days_counted < hold_days:
            if self.is_business_day(current_date):
                business_days_counted += 1
            
            if business_days_counted < hold_days:
                current_date += timedelta(days=1)
        
        # Return datetime with time set to end of day (23:59:59)
        return datetime.combine(current_date, datetime.max.time())
    
    def get_days_remaining(self, expiry_date: datetime) -> int:
        """
        Calculate business days remaining until expiry.
        
        Args:
            expiry_date: Hold expiry date
            
        Returns:
            int: Number of business days remaining (0 or more)
        """
        today = datetime.utcnow().date()
        expiry = expiry_date.date()
        
        if expiry <= today:
            return 0
        
        days_remaining = 0
        current_date = today
        
        while current_date <= expiry:
            if self.is_business_day(current_date):
                days_remaining += 1
            current_date += timedelta(days=1)
        
        # Subtract 1 because we don't count today if it's still valid
        return max(0, days_remaining - 1)
    
    def is_hold_expired(self, expiry_date: datetime) -> bool:
        """
        Check if hold has expired.
        
        Args:
            expiry_date: Hold expiry date
            
        Returns:
            bool: True if hold has expired
        """
        return datetime.utcnow() > expiry_date
    
    def get_business_day_offset(self, start_date: date, offset_days: int) -> date:
        """
        Get date that is offset_days business days away from start_date.
        
        Args:
            start_date: Starting date
            offset_days: Number of business days to offset
            
        Returns:
            date: Date offset by business days
        """
        current_date = start_date
        days_counted = 0
        
        while days_counted < offset_days:
            current_date += timedelta(days=1)
            if self.is_business_day(current_date):
                days_counted += 1
        
        return current_date
    
    def add_business_days(self, start_date: date, days: int) -> date:
        """
        Add business days to a date.
        
        Args:
            start_date: Starting date
            days: Number of business days to add
            
        Returns:
            date: Date after adding business days
        """
        return self.get_business_day_offset(start_date, days)
    
    def get_business_days_count(self, start_date: date, end_date: date) -> int:
        """
        Count business days between two dates (inclusive).
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            int: Number of business days between dates
        """
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        business_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if self.is_business_day(current_date):
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
    
    def add_holidays(self, holidays: List[str]) -> None:
        """
        Add holidays to the calculator.
        
        Args:
            holidays: List of holiday dates in YYYY-MM-DD format
        """
        self._load_holidays(holidays)
    
    def remove_holiday(self, holiday_date: str) -> None:
        """
        Remove a holiday from the calculator.
        
        Args:
            holiday_date: Holiday date in YYYY-MM-DD format
        """
        try:
            date_obj = datetime.strptime(holiday_date, "%Y-%m-%d").date()
            self.holidays.discard(date_obj)
        except ValueError as e:
            logger.warning(f"Invalid holiday format {holiday_date}: {str(e)}")


# Global instance for use throughout the application
business_day_calculator = BusinessDayCalculator()
