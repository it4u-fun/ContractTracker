"""
Custom holidays model for managing user-defined holiday periods.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid

@dataclass
class CustomHoliday:
    """Represents a custom holiday period defined by the user."""
    
    # Holiday identification
    holiday_id: str
    name: str
    start_date: str  # YYYY-MM-DD format
    end_date: str    # YYYY-MM-DD format
    
    # Optional fields with defaults
    description: Optional[str] = None
    holiday_type: str = 'bank_holiday'  # bank_holiday, office_closure, personal_holiday
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        self.updated_at = now
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'holiday_id': self.holiday_id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'holiday_type': self.holiday_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomHoliday':
        """Create CustomHoliday from dictionary."""
        return cls(
            holiday_id=data.get('holiday_id', str(uuid.uuid4())),
            name=data.get('name', ''),
            description=data.get('description'),
            start_date=data.get('start_date', ''),
            end_date=data.get('end_date', ''),
            holiday_type=data.get('holiday_type', 'bank_holiday'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def is_date_in_holiday(self, check_date: str) -> bool:
        """Check if a specific date falls within this holiday period."""
        try:
            check_dt = datetime.strptime(check_date, '%Y-%m-%d').date()
            start_dt = datetime.strptime(self.start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(self.end_date, '%Y-%m-%d').date()
            
            return start_dt <= check_dt <= end_dt
        except ValueError:
            return False
    
    def get_all_dates(self) -> List[str]:
        """Get all dates within this holiday period."""
        dates = []
        try:
            start_dt = datetime.strptime(self.start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(self.end_date, '%Y-%m-%d').date()
            
            current = start_dt
            while current <= end_dt:
                dates.append(current.strftime('%Y-%m-%d'))
                current = date(current.year, current.month, current.day + 1)
            
            return dates
        except ValueError:
            return []
    
    def validate(self) -> List[str]:
        """Validate the holiday data and return any errors."""
        errors = []
        
        if not self.name.strip():
            errors.append("Holiday name is required")
        
        if not self.start_date:
            errors.append("Start date is required")
        elif not self._is_valid_date(self.start_date):
            errors.append("Start date must be in YYYY-MM-DD format")
        
        if not self.end_date:
            errors.append("End date is required")
        elif not self._is_valid_date(self.end_date):
            errors.append("End date must be in YYYY-MM-DD format")
        
        if self._is_valid_date(self.start_date) and self._is_valid_date(self.end_date):
            try:
                start_dt = datetime.strptime(self.start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(self.end_date, '%Y-%m-%d')
                if end_dt < start_dt:
                    errors.append("End date must be after start date")
            except ValueError:
                pass
        
        if self.holiday_type not in ['bank_holiday', 'office_closure', 'personal_holiday']:
            errors.append("Invalid holiday type")
        
        return errors
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if a date string is in valid YYYY-MM-DD format."""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

@dataclass
class CustomHolidayCollection:
    """Collection of custom holidays with management methods."""
    
    holidays: List[CustomHoliday] = None
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        if self.holidays is None:
            self.holidays = []
    
    def add_holiday(self, holiday: CustomHoliday) -> bool:
        """Add a holiday to the collection."""
        errors = holiday.validate()
        if errors:
            return False
        
        # Check for overlapping holidays
        for existing in self.holidays:
            if self._holidays_overlap(holiday, existing):
                return False
        
        self.holidays.append(holiday)
        return True
    
    def remove_holiday(self, holiday_id: str) -> bool:
        """Remove a holiday by ID."""
        original_count = len(self.holidays)
        self.holidays = [h for h in self.holidays if h.holiday_id != holiday_id]
        return len(self.holidays) < original_count
    
    def get_holiday(self, holiday_id: str) -> Optional[CustomHoliday]:
        """Get a holiday by ID."""
        for holiday in self.holidays:
            if holiday.holiday_id == holiday_id:
                return holiday
        return None
    
    def get_holidays_in_range(self, start_date: str, end_date: str) -> List[CustomHoliday]:
        """Get all holidays that overlap with the given date range."""
        overlapping = []
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            for holiday in self.holidays:
                holiday_start = datetime.strptime(holiday.start_date, '%Y-%m-%d').date()
                holiday_end = datetime.strptime(holiday.end_date, '%Y-%m-%d').date()
                
                # Check if holidays overlap
                if not (holiday_end < start_dt or holiday_start > end_dt):
                    overlapping.append(holiday)
            
            return overlapping
        except ValueError:
            return []
    
    def get_all_dates_in_range(self, start_date: str, end_date: str) -> List[str]:
        """Get all holiday dates within the given range."""
        all_dates = []
        for holiday in self.get_holidays_in_range(start_date, end_date):
            all_dates.extend(holiday.get_all_dates())
        return sorted(list(set(all_dates)))  # Remove duplicates and sort
    
    def _holidays_overlap(self, holiday1: CustomHoliday, holiday2: CustomHoliday) -> bool:
        """Check if two holidays overlap."""
        try:
            h1_start = datetime.strptime(holiday1.start_date, '%Y-%m-%d').date()
            h1_end = datetime.strptime(holiday1.end_date, '%Y-%m-%d').date()
            h2_start = datetime.strptime(holiday2.start_date, '%Y-%m-%d').date()
            h2_end = datetime.strptime(holiday2.end_date, '%Y-%m-%d').date()
            
            return not (h1_end < h2_start or h2_end < h1_start)
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'holidays': [holiday.to_dict() for holiday in self.holidays]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomHolidayCollection':
        """Create collection from dictionary."""
        holidays = []
        for holiday_data in data.get('holidays', []):
            holidays.append(CustomHoliday.from_dict(holiday_data))
        
        return cls(holidays=holidays)
