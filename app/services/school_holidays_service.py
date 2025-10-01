import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict

# Source page for official term dates
PRAEWOOD_TERMDATES_URL = 'https://www.praewood.herts.sch.uk/termdatescalendar/term-dates'

HOLIDAY_KEYWORDS = (
    'HALF TERM', 'HOLIDAY', 'TERM ENDS', 'TERM START', 'INSET DAY', 'BANK HOLIDAY'
)

def fetch_terms_page() -> str:
    resp = requests.get(PRAEWOOD_TERMDATES_URL, timeout=20)
    resp.raise_for_status()
    return resp.text

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

def _strip_ordinal(day_str: str) -> str:
    return re.sub(r'(st|nd|rd|th)$', '', day_str)

def _month_to_num(month_name: str) -> int:
    return datetime.strptime(month_name[:3], '%b').month

def _parse_date_fragment(fragment: str, default_year: int) -> datetime:
    # e.g. "27th October 2025" or "27th October"
    parts = fragment.strip().split()
    if len(parts) < 2:
        raise ValueError('Bad date fragment')
    day = int(_strip_ordinal(parts[0]))
    month = _month_to_num(parts[1])
    year = default_year if len(parts) == 2 else int(parts[2])
    return datetime(year, month, day)

def extract_holiday_dates(start_date: str, end_date: str) -> Dict[str, Dict]:
    """Scrape the term-dates page and return date -> {type,label}."""
    html = fetch_terms_page()

    # Find section year markers like "Autumn Term 2025", "Spring Term 2026"
    year_markers = list(re.finditer(r'(Autumn|Spring|Summer)\s+Term\s+(\d{4})', html, re.IGNORECASE))
    # Split the page into blocks per year marker
    blocks = []
    for i, m in enumerate(year_markers):
        start_idx = m.end()
        end_idx = year_markers[i+1].start() if i+1 < len(year_markers) else len(html)
        year = int(m.group(2))
        blocks.append((year, html[start_idx:end_idx]))

    wanted = {}
    window_start = datetime.fromisoformat(start_date)
    window_end = datetime.fromisoformat(end_date)

    # Patterns for half term date ranges
    # e.g. "Half Term 27th October – 31st October 2025"
    range_pat = re.compile(r'Half\s*Term\s+([0-9]{1,2}\w{2}?\s+\w+)\s*[–-]\s*([0-9]{1,2}\w{2}?\s+\w+)(?:\s+(\d{4}))?', re.IGNORECASE)
    # Single day INSET / Public Holiday etc.
    single_pat = re.compile(r'\b(Inset Day|Public Holiday|Occasional Day)\b[^\n\r]*?([0-9]{1,2}\w{2}?\s+\w+\s+\d{4}|[0-9]{1,2}\w{2}?\s+\w+)', re.IGNORECASE)

    for year, block in blocks:
        # Half Term ranges
        for m in range_pat.finditer(block):
            start_frag, end_frag, end_year_opt = m.groups()
            start_dt = _parse_date_fragment(start_frag, year)
            end_year = int(end_year_opt) if end_year_opt else year
            end_dt = _parse_date_fragment(end_frag, end_year)
            # Clip to requested window
            cur = max(start_dt, window_start)
            while cur <= end_dt and cur <= window_end:
                wanted[cur.date().isoformat()] = {'type': 'school_holiday', 'label': 'HALF TERM'}
                cur += timedelta(days=1)

        # Single-day items
        for m in single_pat.finditer(block):
            label, frag = m.groups()
            try:
                dt = _parse_date_fragment(frag, year)
            except Exception:
                continue
            if window_start.date() <= dt.date() <= window_end.date():
                wanted[dt.date().isoformat()] = {'type': 'school_holiday', 'label': label.upper()}

    return wanted


