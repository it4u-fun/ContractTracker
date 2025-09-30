"""
Contract API endpoints
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

from ..models.contract import Contract, DayStatus
from ..services.validation_service import ValidationService
from ..services.suggestion_service import SuggestionService
from ..utils.sanitization import DataSanitizer

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
        # Sanitize contract key
        contract_key = DataSanitizer.sanitize_string(contract_key)
        
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
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Sanitize all input data
        try:
            sanitized_data = DataSanitizer.sanitize_contract_data(data)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f'Data validation error: {str(e)}'
            }), 400
        
        # Create contract with sanitized data
        contract = Contract(
            staff_name=sanitized_data['staff_name'],
            client_company=sanitized_data['client_company'],
            contract_name=sanitized_data['contract_name'],
            start_date=sanitized_data['start_date'],
            end_date=sanitized_data['end_date'],
            total_days=sanitized_data['total_days'],
            daily_rate=sanitized_data['daily_rate']
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
        original_key = DataSanitizer.sanitize_string(contract_key)
        contract = current_app.data_manager.get_contract(original_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        # Check if contract is archived
        if contract.is_archived():
            return jsonify({
                'success': False,
                'error': 'Cannot modify archived contract'
            }), 403
        
        data = request.get_json()
        
        # Update contract fields
        updatable_fields = ['staff_name', 'client_company', 'contract_name',
                           'start_date', 'end_date', 'total_days', 'daily_rate']
        
        for field in updatable_fields:
            if field in data:
                setattr(contract, field, data[field])
        
        # Save updated contract under the original key (preserve key)
        if current_app.data_manager.update_contract_under_key(original_key, contract):
            return jsonify({
                'success': True,
                'contract': contract.to_dict(),
                'contract_key': original_key
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

# Optional: endpoints by id to avoid key issues
@contracts_bp.route('/id/<contract_id>')
def get_contract_by_id(contract_id: str):
    try:
        # Iterate to find contract by id
        contracts = current_app.data_manager.get_all_contracts()
        for key, contract in contracts.items():
            if contract.contract_id == contract_id:
                validation_result = ValidationService.validate_contract(contract)
                return jsonify({'success': True, 'contract': contract.to_dict(), 'validation': validation_result})
        return jsonify({'success': False, 'error': 'Contract not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@contracts_bp.route('/id/<contract_id>', methods=['PUT'])
def update_contract_by_id(contract_id: str):
    try:
        # First try to get contract directly by ID as key
        contracts = current_app.data_manager.get_all_contracts()
        contract = contracts.get(contract_id)
        
        if not contract:
            # Fallback: iterate to find contract by id field
            for key, c in contracts.items():
                if c.contract_id == contract_id:
                    contract = c
                    break
        
        if not contract:
            return jsonify({'success': False, 'error': 'Contract not found'}), 404

        data = request.get_json() or {}
        updatable_fields = ['staff_name', 'client_company', 'contract_name',
                           'start_date', 'end_date', 'total_days', 'daily_rate']
        for field in updatable_fields:
            if field in data:
                setattr(contract, field, data[field])
        
        # Save the updated contract (will use contract_id as key)
        if current_app.data_manager.save_contract(contract):
            return jsonify({'success': True, 'contract': contract.to_dict(), 'contract_id': contract.contract_id})
        return jsonify({'success': False, 'error': 'Failed to update contract'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        # Sanitize contract key
        contract_key = DataSanitizer.sanitize_string(contract_key)
        
        contract = current_app.data_manager.get_contract(contract_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        # Check if contract is archived
        if contract.is_archived():
            return jsonify({
                'success': False,
                'error': 'Cannot modify archived contract'
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Sanitize day allocation data
        try:
            sanitized_data = DataSanitizer.sanitize_day_allocation_data(data)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f'Data validation error: {str(e)}'
            }), 400
        
        # Validate status (restricted to working/holiday)
        try:
            status = DayStatus(sanitized_data['status'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid status: {sanitized_data["status"]}'
            }), 400
        
        # Update day status
        notes = sanitized_data.get('notes')
        contract.set_day_status(sanitized_data['date'], status, notes)
        
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
        
        # Check if contract is archived
        if contract.is_archived():
            return jsonify({
                'success': False,
                'error': 'Cannot modify archived contract'
            }), 403
        
        data = request.get_json()
        suggested_dates = data.get('suggested_dates', [])
        notes_by_date = data.get('notes_by_date', {})
        
        if not suggested_dates:
            return jsonify({
                'success': False,
                'error': 'No suggested dates provided'
            }), 400
        
        # Validate suggested dates are within contract period
        from ..services.calendar_service import CalendarService
        valid_range = set(CalendarService.get_date_range(contract.start_date, contract.end_date))
        filtered_dates = [d for d in suggested_dates if d in valid_range]
        if len(filtered_dates) != len(suggested_dates):
            # If any dates are out of range, return a validation error
            return jsonify({
                'success': False,
                'error': 'One or more suggested dates are outside the contract period'
            }), 400

        # Clear existing working days
        for date_str, day_allocation in list(contract.days.items()):
            if day_allocation.status == DayStatus.WORKING:
                del contract.days[date_str]
        
        # Apply suggested days with optional notes
        for date_str in filtered_dates:
            note = None
            if isinstance(notes_by_date, dict):
                note = notes_by_date.get(date_str)
            contract.set_day_status(date_str, DayStatus.WORKING, note)
        
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

@contracts_bp.route('/<contract_key>/archive', methods=['POST'])
def archive_contract(contract_key: str):
    """Archive a contract."""
    try:
        # Sanitize contract key
        contract_key = DataSanitizer.sanitize_string(contract_key)
        
        contract = current_app.data_manager.get_contract(contract_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        # Archive the contract
        contract.archive()
        
        # Save the updated contract
        if current_app.data_manager.save_contract(contract):
            return jsonify({
                'success': True,
                'message': 'Contract archived successfully',
                'contract': contract.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save archived contract'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/<contract_key>/unarchive', methods=['POST'])
def unarchive_contract(contract_key: str):
    """Unarchive a contract."""
    try:
        # Sanitize contract key
        contract_key = DataSanitizer.sanitize_string(contract_key)
        
        contract = current_app.data_manager.get_contract(contract_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        # Unarchive the contract
        contract.unarchive()
        
        # Save the updated contract
        if current_app.data_manager.save_contract(contract):
            return jsonify({
                'success': True,
                'message': 'Contract unarchived successfully',
                'contract': contract.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save unarchived contract'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@contracts_bp.route('/<contract_key>/fix-out-of-scope', methods=['POST'])
def fix_out_of_scope_allocations(contract_key: str):
    """Remove day allocations that are outside the contract period."""
    try:
        # Sanitize contract key
        contract_key = DataSanitizer.sanitize_string(contract_key)
        
        contract = current_app.data_manager.get_contract(contract_key)
        
        if not contract:
            return jsonify({
                'success': False,
                'error': 'Contract not found'
            }), 404
        
        # Check if contract is archived
        if contract.is_archived():
            return jsonify({
                'success': False,
                'error': 'Cannot modify archived contract'
            }), 403
        
        # Find and remove out-of-scope allocations
        from datetime import datetime
        out_of_scope_dates = []
        
        for date_str in list(contract.days.keys()):
            date = datetime.strptime(date_str, '%Y-%m-%d')
            if date < contract.start_datetime or date > contract.end_datetime:
                out_of_scope_dates.append(date_str)
                del contract.days[date_str]
        
        if not out_of_scope_dates:
            return jsonify({
                'success': True,
                'message': 'No out-of-scope allocations found',
                'removed_dates': []
            })
        
        # Save the updated contract
        if current_app.data_manager.save_contract(contract):
            return jsonify({
                'success': True,
                'message': f'Removed {len(out_of_scope_dates)} out-of-scope day allocation(s)',
                'removed_dates': sorted(out_of_scope_dates),
                'contract': contract.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save updated contract'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
