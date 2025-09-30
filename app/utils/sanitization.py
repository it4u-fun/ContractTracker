"""
Data sanitization utilities for Contract Tracker.
All data MUST be sanitized before being allowed into the Application.
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import bleach


class DataSanitizer:
    """Comprehensive data sanitization class."""
    
    # Allowed HTML tags for rich text (if needed in future)
    ALLOWED_HTML_TAGS = ['b', 'i', 'em', 'strong', 'br']
    
    # Maximum field lengths
    MAX_FIELD_LENGTHS = {
        'staff_name': 100,
        'client_company': 100,
        'contract_name': 200,
        'notes': 1000,
        'setting_name': 100,
        'setting_value': 1000
    }
    
    @staticmethod
    def sanitize_string(value: Any, max_length: Optional[int] = None, allow_html: bool = False) -> str:
        """Sanitize a string value."""
        if value is None:
            return ""
        
        # Convert to string
        value = str(value).strip()
        
        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # HTML escape if not allowing HTML
        if not allow_html:
            value = html.escape(value, quote=True)
        else:
            # Use bleach to sanitize HTML
            value = bleach.clean(value, tags=DataSanitizer.ALLOWED_HTML_TAGS, strip=True)
        
        # Limit length
        if max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def sanitize_contract_key(staff_name: str, client_company: str, contract_name: str) -> str:
        """Generate a sanitized contract key."""
        # Sanitize each component
        staff_safe = DataSanitizer.sanitize_string(staff_name, DataSanitizer.MAX_FIELD_LENGTHS['staff_name'])
        client_safe = DataSanitizer.sanitize_string(client_company, DataSanitizer.MAX_FIELD_LENGTHS['client_company'])
        contract_safe = DataSanitizer.sanitize_string(contract_name, DataSanitizer.MAX_FIELD_LENGTHS['contract_name'])
        
        # Replace non-alphanumeric characters with underscores
        staff_safe = re.sub(r'[^a-zA-Z0-9]', '_', staff_safe)
        client_safe = re.sub(r'[^a-zA-Z0-9]', '_', client_safe)
        contract_safe = re.sub(r'[^a-zA-Z0-9]', '_', contract_safe)
        
        # Remove multiple consecutive underscores
        staff_safe = re.sub(r'_+', '_', staff_safe).strip('_')
        client_safe = re.sub(r'_+', '_', client_safe).strip('_')
        contract_safe = re.sub(r'_+', '_', contract_safe).strip('_')
        
        return f"{staff_safe}_{client_safe}_{contract_safe}"
    
    @staticmethod
    def sanitize_date(value: Any) -> Optional[str]:
        """Sanitize and validate a date string."""
        if not value:
            return None
        
        value = str(value).strip()
        
        # Basic date format validation (YYYY-MM-DD)
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            raise ValueError(f"Invalid date format: {value}. Expected YYYY-MM-DD")
        
        try:
            # Validate the date
            datetime.strptime(value, '%Y-%m-%d')
            return value
        except ValueError as e:
            raise ValueError(f"Invalid date: {value}. {str(e)}")
    
    @staticmethod
    def sanitize_integer(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
        """Sanitize and validate an integer value."""
        if value is None:
            raise ValueError("Integer value cannot be None")
        
        try:
            # Convert to int
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    raise ValueError("Empty string cannot be converted to integer")
            
            int_value = int(value)
            
            # Check bounds
            if min_value is not None and int_value < min_value:
                raise ValueError(f"Value {int_value} is below minimum {min_value}")
            
            if max_value is not None and int_value > max_value:
                raise ValueError(f"Value {int_value} is above maximum {max_value}")
            
            return int_value
            
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid integer: {value}. {str(e)}")
    
    @staticmethod
    def sanitize_contract_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize all contract data."""
        if not isinstance(data, dict):
            raise ValueError("Contract data must be a dictionary")
        
        sanitized = {}
        
        # Required fields with validation
        required_fields = ['staff_name', 'client_company', 'contract_name', 'start_date', 'end_date', 'total_days', 'daily_rate']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Sanitize string fields
        sanitized['staff_name'] = DataSanitizer.sanitize_string(
            data['staff_name'], 
            DataSanitizer.MAX_FIELD_LENGTHS['staff_name']
        )
        sanitized['client_company'] = DataSanitizer.sanitize_string(
            data['client_company'], 
            DataSanitizer.MAX_FIELD_LENGTHS['client_company']
        )
        sanitized['contract_name'] = DataSanitizer.sanitize_string(
            data['contract_name'], 
            DataSanitizer.MAX_FIELD_LENGTHS['contract_name']
        )
        
        # Sanitize dates
        sanitized['start_date'] = DataSanitizer.sanitize_date(data['start_date'])
        sanitized['end_date'] = DataSanitizer.sanitize_date(data['end_date'])
        
        # Validate date order
        if sanitized['start_date'] and sanitized['end_date']:
            start_dt = datetime.strptime(sanitized['start_date'], '%Y-%m-%d')
            end_dt = datetime.strptime(sanitized['end_date'], '%Y-%m-%d')
            if end_dt <= start_dt:
                raise ValueError("End date must be after start date")
        
        # Sanitize integers
        sanitized['total_days'] = DataSanitizer.sanitize_integer(data['total_days'], min_value=1, max_value=365)
        sanitized['daily_rate'] = DataSanitizer.sanitize_integer(data['daily_rate'], min_value=0, max_value=10000)
        
        # Sanitize optional fields
        if 'notes' in data and data['notes']:
            sanitized['notes'] = DataSanitizer.sanitize_string(
                data['notes'], 
                DataSanitizer.MAX_FIELD_LENGTHS['notes']
            )
        
        return sanitized
    
    @staticmethod
    def sanitize_day_allocation_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize day allocation data."""
        if not isinstance(data, dict):
            raise ValueError("Day allocation data must be a dictionary")
        
        sanitized = {}
        
        # Required fields
        if 'date' not in data:
            raise ValueError("Required field 'date' is missing")
        if 'status' not in data:
            raise ValueError("Required field 'status' is missing")
        
        # Sanitize date
        sanitized['date'] = DataSanitizer.sanitize_date(data['date'])
        
        # Sanitize status (must be one of the allowed values)
        allowed_statuses = ['working', 'bank_holiday', 'holiday', 'in_lieu', 'on_call', 'not_applicable']
        status = DataSanitizer.sanitize_string(data['status']).lower()
        if status not in allowed_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(allowed_statuses)}")
        sanitized['status'] = status
        
        # Sanitize optional fields
        if 'is_weekend' in data:
            sanitized['is_weekend'] = bool(data['is_weekend'])
        
        if 'notes' in data and data['notes']:
            sanitized['notes'] = DataSanitizer.sanitize_string(
                data['notes'], 
                DataSanitizer.MAX_FIELD_LENGTHS['notes']
            )
        
        return sanitized
    
    @staticmethod
    def sanitize_setting_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize application setting data."""
        if not isinstance(data, dict):
            raise ValueError("Setting data must be a dictionary")
        
        sanitized = {}
        
        # Required fields
        if 'name' not in data:
            raise ValueError("Required field 'name' is missing")
        if 'value' not in data:
            raise ValueError("Required field 'value' is missing")
        
        # Sanitize name
        sanitized['name'] = DataSanitizer.sanitize_string(
            data['name'], 
            DataSanitizer.MAX_FIELD_LENGTHS['setting_name']
        )
        
        # Sanitize value
        sanitized['value'] = DataSanitizer.sanitize_string(
            data['value'], 
            DataSanitizer.MAX_FIELD_LENGTHS['setting_value']
        )
        
        return sanitized
    
    @staticmethod
    def sanitize_url_path(path: str) -> str:
        """Sanitize URL path components."""
        if not path:
            return ""
        
        # Remove any path traversal attempts
        path = path.replace('..', '').replace('//', '/')
        
        # Remove control characters
        path = re.sub(r'[\x00-\x1F\x7F]', '', path)
        
        # URL encode special characters (this will be handled by Flask, but we sanitize first)
        path = html.escape(path, quote=True)
        
        return path
    
    @staticmethod
    def validate_and_sanitize_api_input(data: Any, expected_type: type, field_name: str = "input") -> Any:
        """Generic API input validation and sanitization."""
        if data is None:
            return None
        
        if not isinstance(data, expected_type):
            raise ValueError(f"{field_name} must be of type {expected_type.__name__}")
        
        if expected_type == str:
            return DataSanitizer.sanitize_string(data)
        elif expected_type == int:
            return DataSanitizer.sanitize_integer(data)
        elif expected_type == dict:
            if not isinstance(data, dict):
                raise ValueError(f"{field_name} must be a dictionary")
            # Return as-is for dict, individual sanitization should be done per field
            return data
        
        return data


def sanitize_all_inputs(func):
    """Decorator to automatically sanitize all inputs to API functions."""
    def wrapper(*args, **kwargs):
        # Sanitize kwargs
        sanitized_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                sanitized_kwargs[key] = DataSanitizer.sanitize_string(value)
            else:
                sanitized_kwargs[key] = value
        
        return func(*args, **sanitized_kwargs)
    
    return wrapper
