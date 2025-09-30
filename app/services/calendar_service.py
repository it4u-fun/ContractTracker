"""
Calendar service for managing calendar operations and date calculations.
"""

import calendar
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional

from ..models.contract import Contract, DayStatus, DayAllocation

class CalendarService:
    """Service for calendar operations and date calculations."""
    
    @staticmethod
    def generate_calendar_grid(year: int, month: int, week_starts_monday: bool = True) -> List[List[Optional[Dict[str, Any]]]]:
        """Generate a calendar grid for the given year and month."""
        cal = calendar.Calendar(firstweekday=0 if week_starts_monday else 6)
        weeks = cal.monthdayscalendar(year, month)
        
        grid = []
        for week in weeks:
            week_days = []
            for day in week:
                if day == 0:
                    week_days.append(None)
                else:
                    date = datetime(year, month, day)
                    week_days.append({
                        'day': day,
                        'date': date.strftime('%Y-%m-%d'),
                        'is_weekend': date.weekday() >= 5,
                        'weekday_name': date.strftime('%A'),
                        'weekday_short': date.strftime('%a'),
                        'month': month,
                        'year': year
                    })
            grid.append(week_days)
        
        return grid
    
    @staticmethod
    def generate_contract_calendar(contract: Contract) -> List[Dict[str, Any]]:
        """Generate calendar data for a contract period."""
        start_date = contract.start_datetime
        end_date = contract.end_datetime
        
        calendar_months = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_grid = CalendarService.generate_calendar_grid(
                current_date.year, 
                current_date.month
            )
            
            calendar_months.append({
                'year': current_date.year,
                'month': current_date.month,
                'month_name': current_date.strftime('%B %Y'),
                'grid': month_grid
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return calendar_months
    
    @staticmethod
    def get_date_range(start_date: str, end_date: str) -> List[str]:
        """Get all dates in a range as YYYY-MM-DD strings."""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return dates
    
    @staticmethod
    def get_weekdays_in_range(start_date: str, end_date: str) -> List[str]:
        """Get all weekdays (Monday-Friday) in a date range."""
        all_dates = CalendarService.get_date_range(start_date, end_date)
        weekdays = []
        
        for date_str in all_dates:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            if date.weekday() < 5:  # Monday=0, Friday=4
                weekdays.append(date_str)
        
        return weekdays
    
    @staticmethod
    def get_weekends_in_range(start_date: str, end_date: str) -> List[str]:
        """Get all weekends (Saturday-Sunday) in a date range."""
        all_dates = CalendarService.get_date_range(start_date, end_date)
        weekends = []
        
        for date_str in all_dates:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            if date.weekday() >= 5:  # Saturday=5, Sunday=6
                weekends.append(date_str)
        
        return weekends
    
    @staticmethod
    def is_weekend(date_str: str) -> bool:
        """Check if a date is a weekend."""
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.weekday() >= 5
    
    @staticmethod
    def get_weekday_name(date_str: str) -> str:
        """Get the weekday name for a date."""
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%A')
    
    @staticmethod
    def format_date(date_str: str, format_str: str = '%d %b %Y') -> str:
        """Format a date string."""
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime(format_str)
    
    @staticmethod
    def get_contract_summary(contract: Contract) -> Dict[str, Any]:
        """Get a summary of contract calendar data."""
        working_days = contract.get_working_days()
        holiday_days = contract.get_days_by_status(DayStatus.HOLIDAY)
        bank_holidays = contract.get_days_by_status(DayStatus.BANK_HOLIDAY)
        
        return {
            'total_working_days': len(working_days),
            'total_holiday_days': len(holiday_days),
            'total_bank_holiday_days': len(bank_holidays),
            'working_days_by_month': CalendarService._group_days_by_month(working_days),
            'holiday_days_by_month': CalendarService._group_days_by_month(holiday_days),
            'bank_holiday_days_by_month': CalendarService._group_days_by_month(bank_holidays),
            'is_balanced': contract.is_balanced,
            'remaining_days': contract.remaining_working_days
        }
    
    @staticmethod
    def _group_days_by_month(days: List[DayAllocation]) -> Dict[str, int]:
        """Group days by month for summary purposes."""
        grouped = {}
        for day in days:
            date = datetime.strptime(day.date, '%Y-%m-%d')
            month_key = f"{date.year}-{date.month:02d}"
            grouped[month_key] = grouped.get(month_key, 0) + 1
        return grouped
    
    @staticmethod
    def get_monthly_breakdown(contract: Contract) -> List[Dict[str, Any]]:
        """Get monthly breakdown of contract days."""
        start_date = contract.start_datetime
        end_date = contract.end_datetime
        
        months = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_end = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])
            
            # Count days in this month
            working_count = 0
            holiday_count = 0
            bank_holiday_count = 0
            
            for day_allocation in contract.days.values():
                day_date = datetime.strptime(day_allocation.date, '%Y-%m-%d')
                if current_date <= day_date <= month_end:
                    if day_allocation.status == DayStatus.WORKING:
                        working_count += 1
                    elif day_allocation.status == DayStatus.HOLIDAY:
                        holiday_count += 1
                    elif day_allocation.status == DayStatus.BANK_HOLIDAY:
                        bank_holiday_count += 1
            
            months.append({
                'year': current_date.year,
                'month': current_date.month,
                'month_name': current_date.strftime('%B %Y'),
                'working_days': working_count,
                'holiday_days': holiday_count,
                'bank_holiday_days': bank_holiday_count,
                'total_days': working_count + holiday_count + bank_holiday_count
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return months
