"""
Data access layer for persisting and retrieving application data.
"""

import json
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.contract import Contract
from ..models.settings import ApplicationSettings
from ..models.custom_holidays import CustomHolidayCollection, CustomHoliday
from ..utils.sanitization import DataSanitizer

class BaseRepository:
    """Base repository class with common JSON persistence functionality."""
    
    def __init__(self, data_dir: str, filename: str):
        """Initialize repository with data directory and filename."""
        self.data_dir = data_dir
        self.filename = filename
        self.filepath = os.path.join(data_dir, filename)
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        if not os.path.exists(self.filepath):
            return {}
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            # Log error and return empty dict
            print(f"Error loading {self.filename}: {e}")
            return {}
    
    def _save_data(self, data: Dict[str, Any]) -> bool:
        """Save data to JSON file."""
        try:
            # Create backup if file exists
            if os.path.exists(self.filepath):
                backup_path = f"{self.filepath}.backup"
                os.rename(self.filepath, backup_path)
            
            # Write new data
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Remove backup on success
            backup_path = f"{self.filepath}.backup"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            return True
            
        except (IOError, OSError) as e:
            # Restore backup on failure
            backup_path = f"{self.filepath}.backup"
            if os.path.exists(backup_path):
                os.rename(backup_path, self.filepath)
            
            print(f"Error saving {self.filename}: {e}")
            return False

class ContractRepository(BaseRepository):
    """Repository for managing contract data."""
    
    def __init__(self, data_dir: str):
        """Initialize contract repository."""
        super().__init__(data_dir, 'contracts.json')
    
    def get_all_contracts(self) -> Dict[str, Contract]:
        """Get all contracts."""
        data = self._load_data()
        contracts = {}
        needs_save = False
        
        for key, contract_data in data.items():
            try:
                contract = Contract.from_dict(contract_data)
                # Ensure contract has an ID (migration for existing contracts)
                if not hasattr(contract, 'contract_id') or contract.contract_id is None:
                    contract.contract_id = str(uuid.uuid4())
                    needs_save = True
                contracts[key] = contract
            except (KeyError, ValueError) as e:
                print(f"Error loading contract {key}: {e}")
                continue
        
        # Save back if we added IDs to existing contracts
        if needs_save:
            self._save_data({k: v.to_dict() for k, v in contracts.items()})
        
        return contracts
    
    def get_contract(self, contract_key: str) -> Optional[Contract]:
        """Get a specific contract by key (contract_id or computed contract_key)."""
        data = self._load_data()
        
        # First try direct lookup by key (could be contract_id or legacy contract_key)
        contract_data = data.get(contract_key)
        
        if contract_data is None:
            # Fallback: search through all contracts to find one with matching computed contract_key
            for k, v in data.items():
                try:
                    if isinstance(v, dict):
                        # Create a temporary contract to compute its contract_key
                        temp_contract = Contract.from_dict(v)
                        if temp_contract.contract_key == contract_key:
                            contract_data = v
                            break
                except Exception:
                    continue
                    
        if contract_data is None:
            return None
        
        try:
            contract = Contract.from_dict(contract_data)
            # Ensure contract has an ID (migration for existing contracts)
            # Only generate new ID if the stored data doesn't have one
            if 'contract_id' not in contract_data or contract_data['contract_id'] is None:
                contract.contract_id = str(uuid.uuid4())
                # Update the existing contract data in place
                contract_data['contract_id'] = contract.contract_id
                # Save the updated data back to the file
                data = self._load_data()
                data[contract_key] = contract_data
                self._save_data(data)
            return contract
        except (KeyError, ValueError) as e:
            print(f"Error loading contract {contract_key}: {e}")
            return None
    
    def save_contract(self, contract: Contract) -> bool:
        """Save a contract with sanitized data."""
        data = self._load_data()
        
        # Use contract_id as key if available, otherwise use sanitized contract_key
        if contract.contract_id:
            key = contract.contract_id
        else:
            key = DataSanitizer.sanitize_string(contract.contract_key)
        
        data[key] = contract.to_dict()
        return self._save_data(data)
    
    def update_contract(self, contract: Contract) -> bool:
        """Update an existing contract."""
        return self.save_contract(contract)  # Same as save for JSON storage
    
    def update_contract_under_key(self, original_key: str, contract: Contract) -> bool:
        """Update a contract but persist under the original key (no rename)."""
        sanitized_key = DataSanitizer.sanitize_string(original_key)
        data = self._load_data()
        data[sanitized_key] = contract.to_dict()
        return self._save_data(data)
    
    def delete_contract(self, contract_key: str) -> bool:
        """Delete a contract with sanitized key."""
        # Sanitize contract key
        sanitized_key = DataSanitizer.sanitize_string(contract_key)
        
        data = self._load_data()
        if sanitized_key in data:
            del data[sanitized_key]
            return self._save_data(data)
        return True  # Already deleted
    
    def contract_exists(self, contract_key: str) -> bool:
        """Check if a contract exists with sanitized key."""
        # Sanitize contract key
        sanitized_key = DataSanitizer.sanitize_string(contract_key)
        
        data = self._load_data()
        return sanitized_key in data
    
    def get_contracts_by_staff(self, staff_name: str) -> List[Contract]:
        """Get all contracts for a specific staff member."""
        all_contracts = self.get_all_contracts()
        return [contract for contract in all_contracts.values() 
                if contract.staff_name == staff_name]
    
    def get_contracts_by_client(self, client_company: str) -> List[Contract]:
        """Get all contracts for a specific client."""
        all_contracts = self.get_all_contracts()
        return [contract for contract in all_contracts.values() 
                if contract.client_company == client_company]

class SettingsRepository(BaseRepository):
    """Repository for managing application settings."""
    
    def __init__(self, data_dir: str):
        """Initialize settings repository."""
        super().__init__(data_dir, 'settings.json')
    
    def get_settings(self) -> ApplicationSettings:
        """Get application settings."""
        data = self._load_data()
        
        if not data:
            return ApplicationSettings()
        
        try:
            return ApplicationSettings.from_dict(data)
        except (KeyError, ValueError) as e:
            print(f"Error loading settings: {e}")
            return ApplicationSettings()
    
    def save_settings(self, settings: ApplicationSettings) -> bool:
        """Save application settings."""
        return self._save_data(settings.to_dict())
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update a specific setting."""
        settings = self.get_settings()
        
        if hasattr(settings, key):
            setattr(settings, key, value)
            settings.updated_at = datetime.now().isoformat()
            return self.save_settings(settings)
        
        return False

class DataManager:
    """Central data manager for coordinating all data operations."""
    
    def __init__(self, data_dir: str):
        """Initialize data manager."""
        self.data_dir = data_dir
        self.contracts = ContractRepository(data_dir)
        self.settings = SettingsRepository(data_dir)
        self.custom_holidays = CustomHolidayRepository(data_dir)
    
    def get_all_contracts(self) -> Dict[str, Contract]:
        """Get all contracts."""
        return self.contracts.get_all_contracts()
    
    def get_contract(self, contract_key: str) -> Optional[Contract]:
        """Get a specific contract."""
        return self.contracts.get_contract(contract_key)
    
    def save_contract(self, contract: Contract) -> bool:
        """Save a contract."""
        return self.contracts.save_contract(contract)
    
    def update_contract_under_key(self, original_key: str, contract: Contract) -> bool:
        """Update a contract stored under a fixed key without renaming the key."""
        return self.contracts.update_contract_under_key(original_key, contract)
    
    def delete_contract(self, contract_key: str) -> bool:
        """Delete a contract."""
        return self.contracts.delete_contract(contract_key)
    
    def get_settings(self) -> ApplicationSettings:
        """Get application settings."""
        return self.settings.get_settings()
    
    def save_settings(self, settings: ApplicationSettings) -> bool:
        """Save application settings."""
        return self.settings.save_settings(settings)
    
    # Custom holidays methods
    def get_custom_holidays(self) -> CustomHolidayCollection:
        """Get all custom holidays."""
        return self.custom_holidays.get_all_holidays()
    
    def add_custom_holiday(self, holiday_data: Dict[str, Any]) -> tuple[bool, str]:
        """Add a new custom holiday."""
        return self.custom_holidays.add_holiday(holiday_data)
    
    def update_custom_holiday(self, holiday_id: str, holiday_data: Dict[str, Any]) -> tuple[bool, str]:
        """Update an existing custom holiday."""
        return self.custom_holidays.update_holiday(holiday_id, holiday_data)
    
    def delete_custom_holiday(self, holiday_id: str) -> tuple[bool, str]:
        """Delete a custom holiday."""
        return self.custom_holidays.delete_holiday(holiday_id)
    
    def get_custom_holidays_in_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get custom holidays within a date range."""
        return self.custom_holidays.get_holidays_in_range(start_date, end_date)
    
    def backup_data(self, backup_dir: str) -> bool:
        """Create a backup of all data."""
        try:
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Backup contracts
            contracts_file = os.path.join(self.data_dir, 'contracts.json')
            if os.path.exists(contracts_file):
                backup_file = os.path.join(backup_dir, f'contracts_{timestamp}.json')
                with open(contracts_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            
            # Backup settings
            settings_file = os.path.join(self.data_dir, 'settings.json')
            if os.path.exists(settings_file):
                backup_file = os.path.join(backup_dir, f'settings_{timestamp}.json')
                with open(settings_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

class CustomHolidayRepository(BaseRepository):
    """Repository for managing custom holiday data."""
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, 'custom_holidays.json')
    
    def get_all_holidays(self) -> CustomHolidayCollection:
        """Get all custom holidays."""
        data = self._load_data()
        if not data:
            return CustomHolidayCollection()
        
        return CustomHolidayCollection.from_dict(data)
    
    def save_holidays(self, holidays: CustomHolidayCollection) -> bool:
        """Save custom holidays collection."""
        try:
            data = holidays.to_dict()
            return self._save_data(data)
        except Exception as e:
            print(f"Error saving custom holidays: {e}")
            return False
    
    def add_holiday(self, holiday_data: Dict[str, Any]) -> tuple[bool, str]:
        """Add a new custom holiday."""
        try:
            # Generate holiday ID if not provided
            if 'holiday_id' not in holiday_data or not holiday_data['holiday_id']:
                holiday_data['holiday_id'] = str(uuid.uuid4())
            
            # Create holiday object
            from ..models.custom_holidays import CustomHoliday
            holiday = CustomHoliday.from_dict(holiday_data)
            
            # Validate
            errors = holiday.validate()
            if errors:
                return False, "; ".join(errors)
            
            # Get existing holidays
            holidays = self.get_all_holidays()
            
            # Check for overlapping holidays
            for existing in holidays.holidays:
                if holidays._holidays_overlap(holiday, existing):
                    return False, "Holiday overlaps with existing holiday period"
            
            # Add holiday
            if holidays.add_holiday(holiday):
                if self.save_holidays(holidays):
                    return True, "Holiday added successfully"
                else:
                    return False, "Failed to save holiday"
            else:
                return False, "Failed to add holiday"
                
        except Exception as e:
            return False, f"Error adding holiday: {str(e)}"
    
    def update_holiday(self, holiday_id: str, holiday_data: Dict[str, Any]) -> tuple[bool, str]:
        """Update an existing custom holiday."""
        try:
            holidays = self.get_all_holidays()
            holiday = holidays.get_holiday(holiday_id)
            
            if not holiday:
                return False, "Holiday not found"
            
            # Update holiday data
            holiday_data['holiday_id'] = holiday_id  # Ensure ID doesn't change
            updated_holiday = CustomHoliday.from_dict(holiday_data)
            
            # Validate
            errors = updated_holiday.validate()
            if errors:
                return False, "; ".join(errors)
            
            # Check for overlapping holidays (excluding current one)
            for existing in holidays.holidays:
                if existing.holiday_id != holiday_id and holidays._holidays_overlap(updated_holiday, existing):
                    return False, "Holiday overlaps with existing holiday period"
            
            # Update in collection
            for i, h in enumerate(holidays.holidays):
                if h.holiday_id == holiday_id:
                    holidays.holidays[i] = updated_holiday
                    break
            
            if self.save_holidays(holidays):
                return True, "Holiday updated successfully"
            else:
                return False, "Failed to save updated holiday"
                
        except Exception as e:
            return False, f"Error updating holiday: {str(e)}"
    
    def delete_holiday(self, holiday_id: str) -> tuple[bool, str]:
        """Delete a custom holiday."""
        try:
            holidays = self.get_all_holidays()
            
            if holidays.remove_holiday(holiday_id):
                if self.save_holidays(holidays):
                    return True, "Holiday deleted successfully"
                else:
                    return False, "Failed to save after deletion"
            else:
                return False, "Holiday not found"
                
        except Exception as e:
            return False, f"Error deleting holiday: {str(e)}"
    
    def get_holidays_in_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get all holidays that overlap with the given date range."""
        try:
            holidays = self.get_all_holidays()
            overlapping = holidays.get_holidays_in_range(start_date, end_date)
            return [holiday.to_dict() for holiday in overlapping]
        except Exception as e:
            print(f"Error getting holidays in range: {e}")
            return []
