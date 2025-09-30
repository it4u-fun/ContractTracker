"""
Suggestion service for generating intelligent day allocation suggestions.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Set, Optional
import random

from ..models.contract import Contract, DayStatus
from .calendar_service import CalendarService

class SuggestionService:
    """Service for generating day allocation suggestions."""
    
    @staticmethod
    def suggest_working_days(contract: Contract, 
                           avoid_weekends: bool = True,
                           avoid_holidays: bool = True,
                           strategy: str = 'balanced') -> List[str]:
        """
        Suggest working days for a contract.
        
        Args:
            contract: The contract to suggest days for
            avoid_weekends: Whether to avoid weekends
            avoid_holidays: Whether to avoid bank holidays
            strategy: Strategy for selection ('balanced', 'front_loaded', 'back_loaded')
        """
        available_dates = SuggestionService._get_available_dates(contract, avoid_weekends, avoid_holidays)
        
        if len(available_dates) < contract.total_days:
            # If not enough available dates, use all available dates
            return available_dates[:contract.total_days]
        
        # Apply selection strategy
        if strategy == 'balanced':
            return SuggestionService._balanced_selection(available_dates, contract.total_days)
        elif strategy == 'front_loaded':
            return SuggestionService._front_loaded_selection(available_dates, contract.total_days)
        elif strategy == 'back_loaded':
            return SuggestionService._back_loaded_selection(available_dates, contract.total_days)
        else:
            return available_dates[:contract.total_days]
    
    @staticmethod
    def _get_available_dates(contract: Contract, 
                           avoid_weekends: bool = True,
                           avoid_holidays: bool = True) -> List[str]:
        """Get available dates for working day allocation."""
        # Start with all dates in contract period
        all_dates = CalendarService.get_date_range(contract.start_date, contract.end_date)
        
        # Filter based on criteria
        available_dates = []
        
        for date_str in all_dates:
            # Check if it's a weekend
            if avoid_weekends and CalendarService.is_weekend(date_str):
                continue
            
            # Check if it's already allocated as a holiday or bank holiday
            existing_day = contract.get_day(date_str)
            if existing_day:
                if avoid_holidays and existing_day.status in [DayStatus.HOLIDAY, DayStatus.BANK_HOLIDAY]:
                    continue
                # Skip if already allocated as working
                if existing_day.status == DayStatus.WORKING:
                    continue
            
            available_dates.append(date_str)
        
        return available_dates
    
    @staticmethod
    def _balanced_selection(available_dates: List[str], total_days: int) -> List[str]:
        """Select days with balanced distribution throughout the period."""
        if len(available_dates) <= total_days:
            return available_dates
        
        # Sort dates
        available_dates.sort()
        
        # Calculate step size for even distribution
        step = len(available_dates) / total_days
        
        selected = []
        for i in range(total_days):
            index = int(i * step)
            if index < len(available_dates):
                selected.append(available_dates[index])
        
        return selected
    
    @staticmethod
    def _front_loaded_selection(available_dates: List[str], total_days: int) -> List[str]:
        """Select days with preference for earlier dates."""
        available_dates.sort()
        return available_dates[:total_days]
    
    @staticmethod
    def _back_loaded_selection(available_dates: List[str], total_days: int) -> List[str]:
        """Select days with preference for later dates."""
        available_dates.sort(reverse=True)
        selected = available_dates[:total_days]
        selected.sort()  # Return in chronological order
        return selected
    
    @staticmethod
    def suggest_holiday_periods(contract: Contract, 
                              total_holiday_days: int,
                              max_period_length: int = 14,
                              min_gap_days: int = 7) -> List[Dict[str, str]]:
        """
        Suggest holiday periods for a contract.
        
        Args:
            contract: The contract to suggest holidays for
            total_holiday_days: Total number of holiday days to suggest
            max_period_length: Maximum days in a single holiday period
            min_gap_days: Minimum gap between holiday periods
        """
        available_dates = SuggestionService._get_holiday_available_dates(contract)
        
        if not available_dates:
            return []
        
        # Group consecutive dates
        periods = SuggestionService._group_consecutive_dates(available_dates)
        
        # Filter periods by max length
        valid_periods = [period for period in periods if len(period) <= max_period_length]
        
        # Select periods to fill total holiday days
        selected_periods = []
        remaining_days = total_holiday_days
        
        for period in valid_periods:
            if remaining_days <= 0:
                break
            
            period_length = min(len(period), remaining_days)
            selected_dates = period[:period_length]
            
            selected_periods.append({
                'start': selected_dates[0],
                'end': selected_dates[-1],
                'days': len(selected_dates)
            })
            
            remaining_days -= period_length
        
        return selected_periods
    
    @staticmethod
    def _get_holiday_available_dates(contract: Contract) -> List[str]:
        """Get dates available for holiday allocation."""
        all_dates = CalendarService.get_date_range(contract.start_date, contract.end_date)
        available_dates = []
        
        for date_str in all_dates:
            existing_day = contract.get_day(date_str)
            if existing_day:
                # Skip if already allocated
                continue
            
            # Prefer weekends and avoid working days
            if not CalendarService.is_weekend(date_str):
                available_dates.append(date_str)
        
        return available_dates
    
    @staticmethod
    def _group_consecutive_dates(dates: List[str]) -> List[List[str]]:
        """Group consecutive dates into periods."""
        if not dates:
            return []
        
        dates.sort()
        periods = []
        current_period = [dates[0]]
        
        for i in range(1, len(dates)):
            current_date = datetime.strptime(dates[i], '%Y-%m-%d')
            prev_date = datetime.strptime(dates[i-1], '%Y-%m-%d')
            
            if (current_date - prev_date).days == 1:
                current_period.append(dates[i])
            else:
                periods.append(current_period)
                current_period = [dates[i]]
        
        periods.append(current_period)
        return periods
    
    @staticmethod
    def suggest_bank_holidays(contract: Contract) -> List[str]:
        """Suggest dates that are likely bank holidays."""
        # This would integrate with external API in a real implementation
        # For now, return common UK bank holidays for the contract period
        return SuggestionService._get_uk_bank_holidays(contract.start_date, contract.end_date)
    
    @staticmethod
    def _get_uk_bank_holidays(start_date: str, end_date: str) -> List[str]:
        """Get UK bank holidays for a date range."""
        # This is a simplified implementation
        # In a real application, this would call an external API
        
        start_year = datetime.strptime(start_date, '%Y-%m-%d').year
        end_year = datetime.strptime(end_date, '%Y-%m-%d').year
        
        bank_holidays = []
        
        for year in range(start_year, end_year + 1):
            # New Year's Day
            bank_holidays.append(f"{year}-01-01")
            
            # Good Friday (approximate - would need proper calculation)
            easter_sunday = SuggestionService._calculate_easter(year)
            good_friday = easter_sunday - timedelta(days=2)
            bank_holidays.append(good_friday.strftime('%Y-%m-%d'))
            
            # Easter Monday
            easter_monday = easter_sunday + timedelta(days=1)
            bank_holidays.append(easter_monday.strftime('%Y-%m-%d'))
            
            # Early May Bank Holiday (first Monday in May)
            may_bank_holiday = datetime(year, 5, 1)
            while may_bank_holiday.weekday() != 0:  # Monday
                may_bank_holiday += timedelta(days=1)
            bank_holidays.append(may_bank_holiday.strftime('%Y-%m-%d'))
            
            # Spring Bank Holiday (last Monday in May)
            spring_bank_holiday = datetime(year, 5, 31)
            while spring_bank_holiday.weekday() != 0:  # Monday
                spring_bank_holiday -= timedelta(days=1)
            bank_holidays.append(spring_bank_holiday.strftime('%Y-%m-%d'))
            
            # Summer Bank Holiday (last Monday in August)
            summer_bank_holiday = datetime(year, 8, 31)
            while summer_bank_holiday.weekday() != 0:  # Monday
                summer_bank_holiday -= timedelta(days=1)
            bank_holidays.append(summer_bank_holiday.strftime('%Y-%m-%d'))
            
            # Christmas Day
            bank_holidays.append(f"{year}-12-25")
            
            # Boxing Day
            bank_holidays.append(f"{year}-12-26")
        
        # Filter to date range
        filtered_holidays = []
        for holiday in bank_holidays:
            if start_date <= holiday <= end_date:
                filtered_holidays.append(holiday)
        
        return filtered_holidays
    
    @staticmethod
    def _calculate_easter(year: int) -> datetime:
        """Calculate Easter Sunday for a given year (simplified algorithm)."""
        # This is a simplified calculation - for production use a proper algorithm
        # or external library
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        n = (h + l - 7 * m + 114) // 31
        p = (h + l - 7 * m + 114) % 31
        
        return datetime(year, n, p + 1)
    
    @staticmethod
    def get_suggestion_summary(contract: Contract) -> Dict[str, Any]:
        """Get a summary of suggestions for a contract."""
        working_suggestions = SuggestionService.suggest_working_days(contract)
        holiday_suggestions = SuggestionService.suggest_holiday_periods(contract, 20)  # 20 holiday days
        bank_holiday_suggestions = SuggestionService.suggest_bank_holidays(contract)
        
        return {
            'working_days_suggested': len(working_suggestions),
            'holiday_periods_suggested': len(holiday_suggestions),
            'bank_holidays_suggested': len(bank_holiday_suggestions),
            'working_days': working_suggestions,
            'holiday_periods': holiday_suggestions,
            'bank_holidays': bank_holiday_suggestions
        }
