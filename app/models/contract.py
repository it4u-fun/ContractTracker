"""
Contract model for managing contract data and business logic.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class DayStatus(Enum):
    """Enumeration of possible day statuses."""
    WORKING = 'working'
    BANK_HOLIDAY = 'bank_holiday'
    HOLIDAY = 'holiday'
    IN_LIEU = 'in_lieu'
    ON_CALL = 'on_call'
    NOT_APPLICABLE = 'not_applicable'

@dataclass
class DayAllocation:
    """Represents a single day allocation within a contract."""
    date: str  # YYYY-MM-DD format
    status: DayStatus
    is_weekend: bool = False
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'date': self.date,
            'status': self.status.value,
            'is_weekend': self.is_weekend,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DayAllocation':
        """Create from dictionary."""
        return cls(
            date=data['date'],
            status=DayStatus(data['status']),
            is_weekend=data.get('is_weekend', False),
            notes=data.get('notes')
        )

@dataclass
class Contract:
    """Represents a contract with all its data and business logic."""
    
    # Contract identification
    staff_name: str
    client_company: str
    contract_name: str
    
    # Contract terms
    start_date: str  # YYYY-MM-DD format
    end_date: str    # YYYY-MM-DD format
    total_days: int
    daily_rate: int
    
    # Day allocations
    days: Dict[str, DayAllocation] = None
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        if self.days is None:
            self.days = {}
        
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        self.updated_at = now
    
    @property
    def contract_key(self) -> str:
        """Generate unique contract key."""
        return f"{self.staff_name}_{self.client_company}_{self.contract_name}"
    
    @property
    def start_datetime(self) -> datetime:
        """Get start date as datetime object."""
        return datetime.strptime(self.start_date, '%Y-%m-%d')
    
    @property
    def end_datetime(self) -> datetime:
        """Get end date as datetime object."""
        return datetime.strptime(self.end_date, '%Y-%m-%d')
    
    @property
    def working_days_count(self) -> int:
        """Count days allocated as working."""
        return sum(1 for day in self.days.values() 
                  if day.status == DayStatus.WORKING)
    
    @property
    def remaining_working_days(self) -> int:
        """Calculate remaining working days to allocate."""
        return self.total_days - self.working_days_count
    
    @property
    def is_balanced(self) -> bool:
        """Check if contract has exactly the required working days."""
        return self.working_days_count == self.total_days
    
    @property
    def total_contract_value(self) -> int:
        """Calculate total contract value."""
        return self.total_days * self.daily_rate
    
    @property
    def earned_value(self) -> int:
        """Calculate earned value based on allocated working days."""
        return self.working_days_count * self.daily_rate
    
    @property
    def predicted_value(self) -> int:
        """Calculate predicted value (same as earned for now)."""
        return self.earned_value
    
    def get_day(self, date: str) -> Optional[DayAllocation]:
        """Get day allocation for a specific date."""
        return self.days.get(date)
    
    def set_day_status(self, date: str, status: DayStatus, notes: Optional[str] = None) -> None:
        """Set the status for a specific day."""
        day = self.days.get(date)
        if day:
            day.status = status
            day.notes = notes
        else:
            # Create new day allocation
            is_weekend = datetime.strptime(date, '%Y-%m-%d').weekday() >= 5
            self.days[date] = DayAllocation(
                date=date,
                status=status,
                is_weekend=is_weekend,
                notes=notes
            )
        
        self.updated_at = datetime.now().isoformat()
    
    def get_days_by_status(self, status: DayStatus) -> List[DayAllocation]:
        """Get all days with a specific status."""
        return [day for day in self.days.values() if day.status == status]
    
    def get_working_days(self) -> List[DayAllocation]:
        """Get all working days."""
        return self.get_days_by_status(DayStatus.WORKING)
    
    def get_holiday_periods(self) -> List[Dict[str, str]]:
        """Get consecutive holiday periods for constraint checking."""
        holiday_days = self.get_days_by_status(DayStatus.HOLIDAY)
        if not holiday_days:
            return []
        
        # Sort by date
        holiday_days.sort(key=lambda x: x.date)
        
        periods = []
        current_period_start = holiday_days[0].date
        
        for i in range(1, len(holiday_days)):
            prev_date = datetime.strptime(holiday_days[i-1].date, '%Y-%m-%d')
            curr_date = datetime.strptime(holiday_days[i].date, '%Y-%m-%d')
            
            # If gap is more than 1 day, end current period
            if (curr_date - prev_date).days > 1:
                periods.append({
                    'start': current_period_start,
                    'end': holiday_days[i-1].date
                })
                current_period_start = holiday_days[i].date
        
        # Add the last period
        periods.append({
            'start': current_period_start,
            'end': holiday_days[-1].date
        })
        
        return periods
    
    def validate_constraints(self) -> List[str]:
        """Validate contract constraints and return list of violations."""
        violations = []
        
        # Check working days balance
        if not self.is_balanced:
            if self.working_days_count > self.total_days:
                violations.append(f"Too many working days: {self.working_days_count} > {self.total_days}")
            else:
                violations.append(f"Insufficient working days: {self.working_days_count} < {self.total_days}")
        
        # Check holiday constraints
        holiday_periods = self.get_holiday_periods()
        for period in holiday_periods:
            start_date = datetime.strptime(period['start'], '%Y-%m-%d')
            end_date = datetime.strptime(period['end'], '%Y-%m-%d')
            period_days = (end_date - start_date).days + 1
            
            if period_days > 14:  # More than 2 weeks
                violations.append(f"Holiday period too long: {period['start']} to {period['end']} ({period_days} days)")
        
        return violations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'staff_name': self.staff_name,
            'client_company': self.client_company,
            'contract_name': self.contract_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'total_days': self.total_days,
            'daily_rate': self.daily_rate,
            'days': {date: day.to_dict() for date, day in self.days.items()},
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contract':
        """Create contract from dictionary."""
        # Convert days dictionary back to DayAllocation objects
        days = {}
        if 'days' in data and data['days']:
            for date, day_data in data['days'].items():
                days[date] = DayAllocation.from_dict(day_data)
        
        return cls(
            staff_name=data['staff_name'],
            client_company=data['client_company'],
            contract_name=data['contract_name'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            total_days=data['total_days'],
            daily_rate=data['daily_rate'],
            days=days,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
