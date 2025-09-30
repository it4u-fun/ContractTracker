"""
Settings model for application configuration and user preferences.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class ApplicationSettings:
    """Application settings and user preferences."""
    
    # Financial settings
    financial_year_start: str = '15-Jul'  # DD-MMM format
    vat_rate: int = 20  # Percentage
    daily_rate: int = 575  # Default daily rate
    
    # Holiday constraints
    max_holiday_weeks: int = 2
    holiday_gap_weeks: int = 1
    
    # Calendar settings
    week_starts_monday: bool = True
    show_weekends: bool = True
    
    # Data source settings
    enabled_data_sources: Dict[str, bool] = None
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        if self.enabled_data_sources is None:
            self.enabled_data_sources = {
                'uk_bank_holidays': True,
                'praewood_school': True,
                'custom_holidays': True
            }
        
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        self.updated_at = now
    
    @property
    def financial_year_start_date(self) -> str:
        """Get financial year start as full date string."""
        current_year = datetime.now().year
        return f"{current_year}-{self.financial_year_start}"
    
    @property
    def vat_rate_decimal(self) -> float:
        """Get VAT rate as decimal (0.2 for 20%)."""
        return self.vat_rate / 100.0
    
    def calculate_vat_amount(self, amount: int) -> int:
        """Calculate VAT amount for a given amount."""
        return int(amount * self.vat_rate_decimal)
    
    def calculate_total_with_vat(self, amount: int) -> int:
        """Calculate total amount including VAT."""
        return amount + self.calculate_vat_amount(amount)
    
    def is_data_source_enabled(self, source_name: str) -> bool:
        """Check if a data source is enabled."""
        return self.enabled_data_sources.get(source_name, False)
    
    def enable_data_source(self, source_name: str) -> None:
        """Enable a data source."""
        self.enabled_data_sources[source_name] = True
        self.updated_at = datetime.now().isoformat()
    
    def disable_data_source(self, source_name: str) -> None:
        """Disable a data source."""
        self.enabled_data_sources[source_name] = False
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'financial_year_start': self.financial_year_start,
            'vat_rate': self.vat_rate,
            'daily_rate': self.daily_rate,
            'max_holiday_weeks': self.max_holiday_weeks,
            'holiday_gap_weeks': self.holiday_gap_weeks,
            'week_starts_monday': self.week_starts_monday,
            'show_weekends': self.show_weekends,
            'enabled_data_sources': self.enabled_data_sources,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApplicationSettings':
        """Create settings from dictionary."""
        return cls(
            financial_year_start=data.get('financial_year_start', '15-Jul'),
            vat_rate=data.get('vat_rate', 20),
            daily_rate=data.get('daily_rate', 575),
            max_holiday_weeks=data.get('max_holiday_weeks', 2),
            holiday_gap_weeks=data.get('holiday_gap_weeks', 1),
            week_starts_monday=data.get('week_starts_monday', True),
            show_weekends=data.get('show_weekends', True),
            enabled_data_sources=data.get('enabled_data_sources', {
                'uk_bank_holidays': True,
                'praewood_school': True,
                'custom_holidays': True
            }),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
