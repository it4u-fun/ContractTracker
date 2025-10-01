## Ways of Working

### Objectives
- **Primary goal**: Keep the Contract Tracker reliable and fast; ship small, verifiable edits.
- **Bias to action**: If blocked, add debug logs or a minimal script to reproduce.

### Environments
- **Local venv**: `.venv` exists.
  - Activate: `source .venv/bin/activate`
  - Install deps: `pip install -r requirements.txt`
- **Docker**: Use helper script `docker-scripts.sh`.
  - Start fresh: `./docker-scripts.sh stop && ./docker-scripts.sh build && ./docker-scripts.sh run`
  - Logs: `docker logs -f contract-tracker`
  - Data volume: `./data` is mounted to `/app/data` in the container.

### Run App
- Local (venv): `FLASK_APP=run.py flask run -p 5000`
- Docker: App served at `http://localhost:5000` after `run`.

### Coding Conventions
- **Python**: Clear, descriptive names; early returns; handle edge cases; minimal inline comments; keep formatting consistent.
- **Type safety**: Annotate public APIs and complex function signatures.
- **Logging**: Prefer concise `print()` server logs while debugging; remove/downgrade after fix.
- **Dates**: Avoid timezone pitfalls. When comparing dates in JS, use local-safe formatting like `YYYY-MM-DD` constructed from Date parts; avoid `toISOString().split('T')[0]` for local calendar logic.

### Frontend Practices
- **Calendar UI**:
  - Inclusive date ranges must include both start and end.
  - Weekend styling: slightly grey by default; green when toggled to working.
  - Month working-days badge updates dynamically on click.
- **APIs**: Use `Utils.apiRequest` and keep endpoints stable. Tooltips should use each flag's `label`.

### Data Sources
- **Custom Holidays**: Inclusive date handling; consistent `T00:00:00` parsing for comparison.
- **UK Bank Holidays**: Fetched via API (existing behavior assumed).
- **PraeWood School Holidays**:
  - Source: `https://www.praewood.herts.sch.uk/termdatescalendar/term-dates`
  - Scraper: `app/services/school_holidays_service.py`
    - Use `User-Agent` header only.
    - Parse labels and adjacent lines; has full-text fallback with ordinal/weekday tolerance.
  - Cache: `data/praewood_dates.json` (merged date-keyed flags: `{ "YYYY-MM-DD": { "type": "school_holiday", "label": "NAME" } }`).
  - API:
    - `POST /api/praewood/sync` → scrape + merge into cache
    - `GET /api/praewood/cache` → full date map
  - Frontend fetch: `static/js/calendar.js` calls `/api/praewood/cache` and filters by range.

### Daily Refresh
- Target: Refresh PraeWood cache daily. For now, manual trigger:
  - `curl -X POST http://localhost:5000/api/praewood/sync`
  - Future: add a lightweight daily job (e.g., cron in host or containerized scheduler).

### Debugging Workflow
- Reproduce quickly: add a `test_*.py` script outside container to isolate logic.
- For scrapers:
  - Print HTML length, sample lines, and parsed counts.
  - Normalize dashes and ordinals; infer years near headings.
- Use docker logs to trace API calls and errors.

### Change Management
- Small, focused edits; keep unrelated changes out.
- After code changes that affect the container:
  - Rebuild + run: `./docker-scripts.sh stop && ./docker-scripts.sh build && ./docker-scripts.sh run`
  - Verify endpoints with `curl`.

### Todos & Status Updates
- Maintain a short, actionable TODO list for multi-step tasks.
- Post micro status updates before/after major actions (e.g., “Rebuilding container…”, “Sync returned 40 dates”).
- Close TODOs once verified; note follow-ups (e.g., cleanup logs).

### PR / Commit Hygiene
- Write commits that explain the “why” succinctly.
- Reference user-visible effects (e.g., “PraeWood sync now ingests 40 dates; tooltips show labels”).

### Useful Commands
```bash
source .venv/bin/activate

# Run scraper locally
python - << 'PY'
from app.services.school_holidays_service import SchoolHolidaysService
svc = SchoolHolidaysService()
print(len(svc.fetch_events_from_website()))
PY

# Trigger PraeWood sync and inspect cache
curl -s -X POST http://localhost:5000/api/praewood/sync | jq .
curl -s http://localhost:5000/api/praewood/cache | jq '{success, total_dates: (.dates | length)}'

# Rebuild & run container
./docker-scripts.sh stop && ./docker-scripts.sh build && ./docker-scripts.sh run
```

### Escalation
- If scraping structure changes, capture a small HTML excerpt in logs and add a targeted parser tweak. Avoid brittle assumptions; prefer tolerant regex + DOM traversal.


