from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from flask import Blueprint, jsonify, request, current_app

from ..services.school_holidays_service import SchoolHolidaysService


praewood_bp = Blueprint("praewood", __name__, url_prefix="/api/praewood")


def _save_full_cache(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Save the entire dates map {date: {type,label}} with updated_at."""
    from ..data.repository import BaseRepository

    class PraeWoodRepository(BaseRepository):
        def __init__(self, data_dir: str):
            super().__init__(data_dir, "praewood_dates.json")

    dm = getattr(current_app, "data_manager", None)
    data_dir = dm.data_dir if dm is not None else current_app.config.get("DATA_DIR", "data")
    repo = PraeWoodRepository(data_dir)

    date_map: Dict[str, Dict[str, str]] = {}
    for e in entries:
        date_map[e["date"]] = {"type": e.get("type", "school_holiday"), "label": e.get("label", "School Holiday")}

    payload = {"dates": date_map, "updated_at": datetime.now().isoformat()}
    repo._save_data(payload)
    return payload


@praewood_bp.route("/sync", methods=["POST"]) 
def sync_praewood_cache():
    """Scrape the full term dates and write the entire cache file."""
    service = SchoolHolidaysService()
    # Scrape all events, then expand to full date flags without limiting by range
    events = service.fetch_events_from_website()
    try:
        print(f"[PraeWood] sync events count={len(events)}")
    except Exception:
        pass
    from datetime import timedelta
    all_flags: List[Dict[str, str]] = []
    for ev in events:
        try:
            start = datetime.strptime(ev["start"], "%Y-%m-%d")
            end = datetime.strptime(ev["end"], "%Y-%m-%d")
        except (KeyError, ValueError):
            continue
        cur = start
        while cur <= end:
            all_flags.append({
                "date": cur.strftime("%Y-%m-%d"),
                "type": "school_holiday",
                "label": ev.get("name", "SCHOOL HOLIDAY").upper(),
            })
            cur = cur + timedelta(days=1)

    try:
        print(f"[PraeWood] sync total flags={len(all_flags)}")
    except Exception:
        pass
    cache = _save_full_cache(all_flags)
    return jsonify({"success": True, "count": len(all_flags), "updated_at": cache.get("updated_at")})


@praewood_bp.route("/cache", methods=["GET"]) 
def get_praewood_cache():
    """Return the entire cached dates map without filtering by range."""
    from ..data.repository import BaseRepository

    class PraeWoodRepository(BaseRepository):
        def __init__(self, data_dir: str):
            super().__init__(data_dir, "praewood_dates.json")

    dm = getattr(current_app, "data_manager", None)
    data_dir = dm.data_dir if dm is not None else current_app.config.get("DATA_DIR", "data")
    repo = PraeWoodRepository(data_dir)
    data = repo._load_data() or {"dates": {}, "updated_at": None}
    # If cache empty, attempt to sync once automatically
    if not data.get("dates"):
        try:
            response = sync_praewood_cache()
            # Reload after sync
            data = repo._load_data() or {"dates": {}, "updated_at": None}
        except Exception as e:
            print(f"PraeWood auto-sync failed: {e}")
    return jsonify({"success": True, **data})


