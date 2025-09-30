"""
Data access layer for persisting and retrieving application data.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.contract import Contract
from ..models.settings import ApplicationSettings
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
        
        for key, contract_data in data.items():
            try:
                contracts[key] = Contract.from_dict(contract_data)
            except (KeyError, ValueError) as e:
                print(f"Error loading contract {key}: {e}")
                continue
        
        return contracts
    
    def get_contract(self, contract_key: str) -> Optional[Contract]:
        """Get a specific contract by key."""
        data = self._load_data()
        contract_data = data.get(contract_key)
        
        if contract_data is None:
            return None
        
        try:
            return Contract.from_dict(contract_data)
        except (KeyError, ValueError) as e:
            print(f"Error loading contract {contract_key}: {e}")
            return None
    
    def save_contract(self, contract: Contract) -> bool:
        """Save a contract with sanitized data."""
        # Sanitize contract key before using it
        sanitized_key = DataSanitizer.sanitize_string(contract.contract_key)
        
        data = self._load_data()
        data[sanitized_key] = contract.to_dict()
        return self._save_data(data)
    
    def update_contract(self, contract: Contract) -> bool:
        """Update an existing contract."""
        return self.save_contract(contract)  # Same as save for JSON storage
    
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
    
    def get_all_contracts(self) -> Dict[str, Contract]:
        """Get all contracts."""
        return self.contracts.get_all_contracts()
    
    def get_contract(self, contract_key: str) -> Optional[Contract]:
        """Get a specific contract."""
        return self.contracts.get_contract(contract_key)
    
    def save_contract(self, contract: Contract) -> bool:
        """Save a contract."""
        return self.contracts.save_contract(contract)
    
    def delete_contract(self, contract_key: str) -> bool:
        """Delete a contract."""
        return self.contracts.delete_contract(contract_key)
    
    def get_settings(self) -> ApplicationSettings:
        """Get application settings."""
        return self.settings.get_settings()
    
    def save_settings(self, settings: ApplicationSettings) -> bool:
        """Save application settings."""
        return self.settings.save_settings(settings)
    
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
