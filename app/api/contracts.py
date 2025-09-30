"""
Contract API endpoints
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

from ..models.contract import Contract, DayStatus
from ..services.validation_service import ValidationService
from ..services.suggestion_service import SuggestionService

contracts_bp = Blueprint('contracts', __name__)

@contracts_bp.route('/')
def get_all_contracts():
    """Get all contracts."""
    try:
        contracts = current_app.data_manager.get_all_contracts()
        
        # Convert to API format
        contracts_data = {}
        for key, contract in contracts.items():
            contracts_data[key] = {
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
                'created_at': contract.created_at,
                'updated_at': contract.updated_at
            }
        
        return jsonify({
            'success': True,
            'contracts': contracts_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/<contract_key>')
def get_contract(contract_key: str):
    """Get a specific contract."""
    try:
        contract = current_app.data_manager.get_contract(contract_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        # Get validation results
        validation_result = ValidationService.validate_contract(contract)
        
        return jsonify({
            'success': True,
            'contract': contract.to_dict(),
            'validation': validation_result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/', methods=['POST'])
def create_contract():
    """Create a new contract."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['staff_name', 'client_company', 'contract_name', 
                          'start_date', 'end_date', 'total_days', 'daily_rate']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create contract
        contract = Contract(
            staff_name=data['staff_name'],
            client_company=data['client_company'],
            contract_name=data['contract_name'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            total_days=data['total_days'],
            daily_rate=data['daily_rate']
        )
        
        # Check if contract already exists
        if current_app.data_manager.contracts.contract_exists(contract.contract_key):
            return jsonify({
                'success': False,
                'error': 'Contract already exists'
            }), 409
        
        # Save contract
        if current_app.data_manager.save_contract(contract):
            return jsonify({
                'success': True,
                'contract': contract.to_dict(),
                'contract_key': contract.contract_key
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save contract'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/<contract_key>', methods=['PUT'])
def update_contract(contract_key: str):
    """Update an existing contract."""
    try:
        contract = current_app.data_manager.get_contract(contract_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        data = request.get_json()
        
        # Update contract fields
        updatable_fields = ['staff_name', 'client_company', 'contract_name',
                           'start_date', 'end_date', 'total_days', 'daily_rate']
        
        for field in updatable_fields:
            if field in data:
                setattr(contract, field, data[field])
        
        # Save updated contract
        if current_app.data_manager.save_contract(contract):
            return jsonify({
                'success': True,
                'contract': contract.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update contract'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/<contract_key>', methods=['DELETE'])
def delete_contract(contract_key: str):
    """Delete a contract."""
    try:
        if not current_app.data_manager.contracts.contract_exists(contract_key):
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        if current_app.data_manager.delete_contract(contract_key):
            return jsonify({
                'success': True,
                'message': 'Contract deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete contract'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/<contract_key>/days', methods=['POST'])
def update_day_status(contract_key: str):
    """Update the status of a specific day."""
    try:
        contract = current_app.data_manager.get_contract(contract_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        data = request.get_json()
        
        if 'date' not in data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: date, status'
            }), 400
        
        # Validate status
        try:
            status = DayStatus(data['status'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid status: {data["status"]}'
            }), 400
        
        # Update day status
        notes = data.get('notes')
        contract.set_day_status(data['date'], status, notes)
        
        # Save contract
        if current_app.data_manager.save_contract(contract):
            # Get validation results
            validation_result = ValidationService.validate_contract(contract)
            
            return jsonify({
                'success': True,
                'working_days_count': contract.working_days_count,
                'remaining_days': contract.remaining_working_days,
                'is_balanced': contract.is_balanced,
                'validation': validation_result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save contract'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/<contract_key>/suggestions', methods=['GET'])
def get_suggestions(contract_key: str):
    """Get suggestions for a contract."""
    try:
        contract = current_app.data_manager.get_contract(contract_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        # Get suggestion parameters from query string
        avoid_weekends = request.args.get('avoid_weekends', 'true').lower() == 'true'
        avoid_holidays = request.args.get('avoid_holidays', 'true').lower() == 'true'
        strategy = request.args.get('strategy', 'balanced')
        
        # Generate suggestions
        suggestions = SuggestionService.suggest_working_days(
            contract, avoid_weekends, avoid_holidays, strategy
        )
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'count': len(suggestions)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/<contract_key>/suggestions', methods=['POST'])
def apply_suggestions(contract_key: str):
    """Apply suggestions to a contract."""
    try:
        contract = current_app.data_manager.get_contract(contract_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        data = request.get_json()
        suggested_dates = data.get('suggested_dates', [])
        
        if not suggested_dates:
            return jsonify({
                'success': False,
                'error': 'No suggested dates provided'
            }), 400
        
        # Clear existing working days
        for date_str, day_allocation in list(contract.days.items()):
            if day_allocation.status == DayStatus.WORKING:
                del contract.days[date_str]
        
        # Apply suggested days
        for date_str in suggested_dates:
            contract.set_day_status(date_str, DayStatus.WORKING)
        
        # Save contract
        if current_app.data_manager.save_contract(contract):
            validation_result = ValidationService.validate_contract(contract)
            
            return jsonify({
                'success': True,
                'working_days_count': contract.working_days_count,
                'remaining_days': contract.remaining_working_days,
                'is_balanced': contract.is_balanced,
                'validation': validation_result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save contract'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/<contract_key>/validate', methods=['GET'])
def validate_contract(contract_key: str):
    """Validate a contract."""
    try:
        contract = current_app.data_manager.get_contract(contract_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        validation_result = ValidationService.validate_contract(contract)
        health_score = ValidationService.get_contract_health_score(contract)
        
        return jsonify({
            'success': True,
            'validation': validation_result,
            'health_score': health_score
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
