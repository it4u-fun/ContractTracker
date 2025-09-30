"""
Dashboard API endpoints
"""

from flask import Blueprint, jsonify, current_app
from ..utils.sanitization import DataSanitizer

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    """Get dashboard data."""
    try:
        contracts = current_app.data_manager.get_all_contracts()
        settings = current_app.data_manager.get_settings()
        
        # Calculate dashboard statistics
        total_contracts = len(contracts)
        total_value = sum(contract.total_contract_value for contract in contracts.values())
        total_earned = sum(contract.earned_value for contract in contracts.values())
        
        # Get contract summaries
        contract_summaries = []
        for key, contract in contracts.items():
            from ..services.validation_service import ValidationService
            validation_result = ValidationService.validate_contract(contract)
            health_score = ValidationService.get_contract_health_score(contract)
            
            contract_summaries.append({
                'key': key,
                'staff_name': contract.staff_name,
                'client_company': contract.client_company,
                'contract_name': contract.contract_name,
                'start_date': contract.start_date,
                'end_date': contract.end_date,
                'total_days': contract.total_days,
                'daily_rate': contract.daily_rate,
                'working_days_count': contract.working_days_count,
                'remaining_days': contract.remaining_working_days,
                'is_balanced': contract.is_balanced,
                'total_value': contract.total_contract_value,
                'earned_value': contract.earned_value,
                'progress_percentage': (contract.working_days_count / contract.total_days * 100) if contract.total_days > 0 else 0,
                'health_score': health_score,
                'validation': validation_result,
                'created_at': contract.created_at,
                'updated_at': contract.updated_at
            })
        
        return jsonify({
            'success': True,
            'dashboard': {
                'total_contracts': total_contracts,
                'total_value': total_value,
                'total_earned': total_earned,
                'total_remaining': total_value - total_earned,
                'contracts': contract_summaries
            },
            'settings': settings.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get application settings."""
    try:
        settings = current_app.data_manager.get_settings()
        
        return jsonify({
            'success': True,
            'settings': settings.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/settings', methods=['PUT'])
def update_settings():
    """Update application settings."""
    try:
        from flask import request
        from ..models.settings import ApplicationSettings
        
        data = request.get_json()
        
        # Get current settings
        settings = current_app.data_manager.get_settings()
        
        # Update settings
        updatable_fields = [
            'financial_year_start', 'vat_rate', 'daily_rate',
            'max_holiday_weeks', 'holiday_gap_weeks',
            'week_starts_monday', 'show_weekends', 'enabled_data_sources'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(settings, field, data[field])
        
        # Save settings
        if current_app.data_manager.save_settings(settings):
            return jsonify({
                'success': True,
                'settings': settings.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save settings'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
