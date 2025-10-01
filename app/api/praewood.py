from flask import Blueprint, jsonify, request, current_app
import requests
from datetime import datetime, timedelta
from ..services.school_holidays_service import extract_holiday_dates

praewood_bp = Blueprint('praewood', __name__, url_prefix='/api/praewood')

SCHOOLJOTTER_URL = 'https://api.schooljotter3.com/api/events_occurrences'
SCHOOLJOTTER_HEADERS = {
    'accept': 'application/json',
    'origin': 'https://www.praewood.herts.sch.uk',
    'user-agent': 'ContractTracker/1.0 (+https://localhost)',
    'x-tenant': 'c4547ee8-0cc9-46b4-88ad-fdaf3e9788a8',
    'x-timezone': 'Europe/London',
}

def _fetch_events(start_date: str, end_date: str):
    params = {'start_date': start_date, 'end_date': end_date}
    resp = requests.get(SCHOOLJOTTER_URL, params=params, headers=SCHOOLJOTTER_HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()

@praewood_bp.route('/events', methods=['GET'])
def events():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not start_date or not end_date:
        return jsonify({'success': False, 'error': 'start_date and end_date are required (YYYY-MM-DD)'}), 400
    try:
        data = _fetch_events(start_date, end_date)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 502

@praewood_bp.route('/types', methods=['GET'])
def list_types():
    # default: last 12 months
    months = int(request.args.get('months', '12'))
    end = datetime.utcnow().date()
    start = end - timedelta(days=months*30)
    try:
        data = _fetch_events(start.isoformat(), end.isoformat())
        names = set()
        for item in data.get('result', []):
            name = (item.get('name') or '').strip()
            if name:
                names.add(name)
        return jsonify({'success': True, 'months': months, 'distinct_names': sorted(names)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 502

@praewood_bp.route('/flags', methods=['GET'])
def flags():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not start_date or not end_date:
        return jsonify({'success': False, 'error': 'start_date and end_date are required (YYYY-MM-DD)'}), 400
    try:
        flags = extract_holiday_dates(start_date, end_date)
        # Merge into cache
        current_app.data_manager.merge_praewood_dates(flags)
        # Respond with rich details
        sorted_items = sorted(flags.items())
        return jsonify({'success': True, 'flags': [{ 'date': d, **details } for d, details in sorted_items]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 502


