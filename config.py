"""
Configuration settings for the Contract Tracker application.
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration class."""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Data storage settings
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    CONTRACTS_FILE = os.path.join(DATA_DIR, 'contracts.json')
    SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
    
    # Default settings
    DEFAULT_SETTINGS = {
        'financial_year_start': '15-Jul',
        'vat_rate': 20,
        'daily_rate': 575,
        'max_holiday_weeks': 2
    }
    
    # Day status configuration
    DAY_STATUSES = {
        'working': {
            'name': 'Working',
            'color': '#d4edda',
            'icon': 'fas fa-briefcase'
        },
        'bank_holiday': {
            'name': 'Bank Holiday/Office Shut',
            'color': '#fff3cd',
            'icon': 'fas fa-calendar-times'
        },
        'holiday': {
            'name': 'Holiday / Sick',
            'color': '#f8d7da',
            'icon': 'fas fa-umbrella-beach'
        },
        'in_lieu': {
            'name': 'In Lieu (off but paid)',
            'color': '#d1ecf1',
            'icon': 'fas fa-balance-scale'
        },
        'on_call': {
            'name': 'On Call / Carry Over Time',
            'color': '#e2e3e5',
            'icon': 'fas fa-phone'
        },
        'not_applicable': {
            'name': 'Not Applicable',
            'color': '#f8f9fa',
            'icon': 'fas fa-minus'
        }
    }
    
    # API endpoints for external data
    EXTERNAL_APIS = {
        'uk_bank_holidays': 'https://www.gov.uk/bank-holidays.json',
        'school_holidays': {
            'praewood': {
                'name': 'PraeWood School',
                'region': 'Hertfordshire',
                'url': None  # To be implemented
            }
        }
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests', 'test_data')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
