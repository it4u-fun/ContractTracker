import requests
from datetime import datetime, timedelta
from typing import List, Dict

SCHOOLJOTTER_URL = 'https://api.schooljotter3.com/api/events_occurrences'
SCHOOLJOTTER_HEADERS = {
    'accept': 'application/json',
    'origin': 'https://www.praewood.herts.sch.uk',
    'user-agent': 'ContractTracker/1.0 (+https://localhost)',
    'x-tenant': 'c4547ee8-0cc9-46b4-88ad-fdaf3e9788a8',
    'x-timezone': 'Europe/London',
}

HOLIDAY_KEYWORDS = (
    'HALF TERM', 'HOLIDAY', 'TERM ENDS', 'TERM START', 'INSET DAY', 'BANK HOLIDAY'
)

def fetch_events(start_date: str, end_date: str) -> Dict:
    params = {'start_date': start_date, 'end_date': end_date}
    resp = requests.get(SCHOOLJOTTER_URL, params=params, headers=SCHOOLJOTTER_HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()

def expand_dates(start_iso: str, end_iso: str) -> List[str]:
    # Normalize to date portion in Europe/London (api already offsets).
    start = datetime.fromisoformat(start_iso.replace('Z', '+00:00')).date()
    end = datetime.fromisoformat(end_iso.replace('Z', '+00:00')).date()
    dates = []
    current = start
    while current <= end:
        dates.append(current.isoformat())
        current += timedelta(days=1)
    return dates

def extract_holiday_dates(start_date: str, end_date: str) -> Dict[str, Dict]:
    """Return dict of date -> {'type': 'school_holiday', 'label': name} for closures."""
    data = fetch_events(start_date, end_date)
    flags: Dict[str, Dict] = {}
    for item in data.get('result', []):
        name = (item.get('name') or '').strip()
        if not name:
            continue
        if not any(keyword in name.upper() for keyword in HOLIDAY_KEYWORDS):
            continue
        occur = item.get('occurences') or []
        for occ in occur:
            s = occ.get('start')
            e = occ.get('end')
            if not s or not e:
                continue
            for d in expand_dates(s, e):
                flags[d] = {'type': 'school_holiday', 'label': name}
    return flags


