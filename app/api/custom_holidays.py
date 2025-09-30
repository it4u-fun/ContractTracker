"""
API endpoints for managing custom holiday data sources.
"""

from flask import Blueprint, request, jsonify, current_app
from ..utils.sanitization import DataSanitizer

custom_holidays_bp = Blueprint('custom_holidays', __name__)

@custom_holidays_bp.route('/api/custom-holidays', methods=['GET'])
def get_custom_holidays():
    """Get all custom holidays."""
    try:
        holidays = current_app.data_manager.get_custom_holidays()
        return jsonify({
            'success': True,
            'holidays': [holiday.to_dict() for holiday in holidays.holidays]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@custom_holidays_bp.route('/api/custom-holidays', methods=['POST'])
def add_custom_holiday():
    """Add a new custom holiday."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Sanitize input data
        sanitized_data = {
            'name': DataSanitizer.sanitize_string(data.get('name', ''), 100),
            'description': DataSanitizer.sanitize_string(data.get('description', ''), 500) if data.get('description') else None,
            'start_date': DataSanitizer.sanitize_date(data.get('start_date', '')),
            'end_date': DataSanitizer.sanitize_date(data.get('end_date', '')),
            'holiday_type': DataSanitizer.sanitize_string(data.get('holiday_type', 'bank_holiday'), 50)
        }
        
        # Validate holiday type
        valid_types = ['bank_holiday', 'office_closure', 'personal_holiday']
        if sanitized_data['holiday_type'] not in valid_types:
            sanitized_data['holiday_type'] = 'bank_holiday'
        
        success, message = current_app.data_manager.add_custom_holiday(sanitized_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@custom_holidays_bp.route('/api/custom-holidays/<holiday_id>', methods=['PUT'])
def update_custom_holiday(holiday_id: str):
    """Update an existing custom holiday."""
    try:
        # Sanitize holiday ID
        holiday_id = DataSanitizer.sanitize_string(holiday_id)
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Sanitize input data
        sanitized_data = {
            'name': DataSanitizer.sanitize_string(data.get('name', ''), 100),
            'description': DataSanitizer.sanitize_string(data.get('description', ''), 500) if data.get('description') else None,
            'start_date': DataSanitizer.sanitize_date(data.get('start_date', '')),
            'end_date': DataSanitizer.sanitize_date(data.get('end_date', '')),
            'holiday_type': DataSanitizer.sanitize_string(data.get('holiday_type', 'bank_holiday'), 50)
        }
        
        # Validate holiday type
        valid_types = ['bank_holiday', 'office_closure', 'personal_holiday']
        if sanitized_data['holiday_type'] not in valid_types:
            sanitized_data['holiday_type'] = 'bank_holiday'
        
        success, message = current_app.data_manager.update_custom_holiday(holiday_id, sanitized_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@custom_holidays_bp.route('/api/custom-holidays/<holiday_id>', methods=['DELETE'])
def delete_custom_holiday(holiday_id: str):
    """Delete a custom holiday."""
    try:
        # Sanitize holiday ID
        holiday_id = DataSanitizer.sanitize_string(holiday_id)
        
        success, message = current_app.data_manager.delete_custom_holiday(holiday_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@custom_holidays_bp.route('/api/custom-holidays/range', methods=['GET'])
def get_holidays_in_range():
    """Get custom holidays within a date range."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({
                'success': False,
                'error': 'start_date and end_date parameters are required'
            }), 400
        
        # Sanitize dates
        start_date = DataSanitizer.sanitize_date(start_date)
        end_date = DataSanitizer.sanitize_date(end_date)
        
        holidays = current_app.data_manager.get_custom_holidays_in_range(start_date, end_date)
        
        return jsonify({
            'success': True,
            'holidays': holidays
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
