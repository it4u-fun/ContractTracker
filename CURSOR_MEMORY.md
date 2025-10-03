# CURSOR_MEMORY.md - Contract Tracker Development Guide

This file contains all the essential information for working with the Contract Tracker project, combining onboarding guidance with detailed ways of working.

## What this app is
- **Purpose**: Track contractor working days, validate constraints, and forecast earnings.
- **Stack**: Python Flask backend with HTML/JS frontend. Packaged and run via **Docker/Docker Compose**.
- **Data**: JSON files persisted under `./data` (mounted as a Docker volume).

## Objectives
- **Primary goal**: Keep the Contract Tracker reliable and fast; ship small, verifiable edits.
- **Bias to action**: If blocked, add debug logs or a minimal script to reproduce.

## Environments

### Local venv
- **Local venv**: `.venv` exists.
  - Activate: `source .venv/bin/activate`
  - Install deps: `pip install -r requirements.txt`
- **Run App**: `FLASK_APP=run.py flask run -p 5000`

### Docker (Recommended)
- **Docker**: Use helper script `docker-scripts.sh`.
  - Start fresh: `./docker-scripts.sh stop && ./docker-scripts.sh build && ./docker-scripts.sh run`
  - Logs: `docker logs -f contract-tracker`
  - Data volume: `./data` is mounted to `/app/data` in the container.
- **Run with Docker Compose**:
  ```bash
  docker-compose up -d                   # App + data volume
  docker-compose --profile with-nginx up -d  # With nginx reverse proxy
  ```
- **Access**: Web UI at `http://localhost:5000`

Notes:
- The script auto-creates `./data` for persistence.
- Environment variables like `FLASK_ENV` and `SECRET_KEY` are set in the container (see `docker-scripts.sh`). For production, configure securely and prefer `Dockerfile.prod`/compose profiles.

## Application Structure
```
ContractTracker/
├─ app/                    # Python package
│  ├─ api/                 # Flask routes (REST endpoints)
│  ├─ models/              # Data models & settings
│  ├─ services/            # Business logic (calendar, suggestions, validation)
│  └─ data/                # Repository/data access helpers
├─ templates/              # Jinja2 HTML templates
├─ static/                 # Frontend JS/CSS/images
├─ data/                   # Runtime JSON storage (mounted in Docker)
├─ run.py                  # App entrypoint
├─ docker-scripts.sh       # Build/run/manage helpers for Docker
└─ docker-compose.yml      # Compose orchestration
```

## API Quick Reference
- Base URL (dev): `http://localhost:5000/api`
- Core endpoints: `GET/POST /api/contracts/`, `GET/PUT/DELETE /api/contracts/{key}`
- Day ops: `POST /api/contracts/{key}/days`, suggestions `GET/POST /api/contracts/{key}/suggestions`, validate `GET /api/contracts/{key}/validate`
- Dashboard/settings: `GET /api/dashboard/`, `GET/PUT /api/dashboard/settings`
- See `API.md` for request/response details.

## Coding Conventions

### Python
- Clear, descriptive names; early returns; handle edge cases; minimal inline comments; keep formatting consistent.
- **Type safety**: Annotate public APIs and complex function signatures.
- **Logging**: Prefer concise `print()` server logs while debugging; remove/downgrade after fix.
- **Dates**: Avoid timezone pitfalls. When comparing dates in JS, use local-safe formatting like `YYYY-MM-DD` constructed from Date parts; avoid `toISOString().split('T')[0]` for local calendar logic.

### Frontend Practices
- **Calendar UI**:
  - Inclusive date ranges must include both start and end.
  - Weekend styling: slightly grey by default; green when toggled to working.
  - Month working-days badge updates dynamically on click.
  - **Current Date Highlighting**: Red border with "TODAY" label for current date
  - **Past Days Styling**: Use 70% opacity to distinguish past days while maintaining full interactivity
- **APIs**: Use `Utils.apiRequest` and keep endpoints stable. Tooltips should use each flag's `label`.
- **JavaScript Date Handling**: Use `isCurrentDate()` and `isPastDate()` methods for consistent date comparisons

## Data Sources

### Custom Holidays
- Inclusive date handling; consistent `T00:00:00` parsing for comparison.

### UK Bank Holidays
- Fetched via API (existing behavior assumed).

### PraeWood School Holidays
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

## Debugging Workflow
- Reproduce quickly: add a `test_*.py` script outside container to isolate logic.
- For scrapers:
  - Print HTML length, sample lines, and parsed counts.
  - Normalize dashes and ordinals; infer years near headings.
- Use docker logs to trace API calls and errors.

## Change Management
- Small, focused edits; keep unrelated changes out.
- After code changes that affect the container:
  - Rebuild + run: `./docker-scripts.sh stop && ./docker-scripts.sh build && ./docker-scripts.sh run`
  - Verify endpoints with `curl`.
- **Browser Cache Issues**: When JavaScript/CSS changes don't appear, restart Flask server to force cache refresh
- **Container Management**: Use `docker start contract-tracker` to restart existing container instead of rebuilding

## Testing with the Chrome Agent
- Start the app (Docker or local), then use the Chrome agent to:
  - Navigate to `http://localhost:5000` and exercise UI flows
  - Capture snapshots/screenshots and read console/network logs
  - Run performance traces and analyze Core Web Vitals
- This is useful for automated/regression checks of pages like `dashboard`, `contracts`, and `settings`.

## Ways of Working
- Use Docker via `docker-scripts.sh` for build/run; keep the app running and healthy.
- Test changes end-to-end: rebuild, run, then verify UI/API; fix regressions immediately.
- Use the Chrome agent to validate UI states, console/network, and performance.
- Keep documentation concise and current in `CURSOR_MEMORY.md`, `README.md`, and `API.md`.
- Prefer conventional commits and small, focused edits.
- **Debugging workflow**: When issues arise, use Chrome agent to reproduce, check Docker logs, and test fixes systematically.
- **Data integrity**: Always verify changes in the actual data files (`./data/*.json`) and test with real data.
- **Cross-browser compatibility**: Test JavaScript fixes with timezone-safe date handling and proper weekday calculations.

## Todos & Status Updates
- Maintain a short, actionable TODO list for multi-step tasks.
- Post micro status updates before/after major actions (e.g., "Rebuilding container…", "Sync returned 40 dates").
- Close TODOs once verified; note follow-ups (e.g., cleanup logs).

## Git Workflow (docs-first)
Always update relevant docs alongside code changes, then commit:
```bash
git add -A
git commit -m "docs: update CURSOR_MEMORY and related docs; feat/fix: <short summary>"
git push origin <your-branch>
```
Prefer conventional commit prefixes (e.g., `feat:`, `fix:`, `docs:`, `refactor:`) and keep `README.md`/`API.md` in sync with behavior changes.

## PR / Commit Hygiene
- Write commits that explain the "why" succinctly.
- Reference user-visible effects (e.g., "PraeWood sync now ingests 40 dates; tooltips show labels").

## Conventions
- Keep data sanitized and validated across layers (see `app/utils/sanitization.py` and validation services).
- Prefer Docker workflows for parity; use Compose profiles for nginx.
- Submit changes with clear descriptions and keep API/README updated.
- You rebuild container, run the new code, and then Test your changes have been successful. Look for any issues that may have introduced bugs. If found, fix them. Keep the Application in running, working order.

## Useful Commands
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

# Restart existing container (faster than rebuild)
docker start contract-tracker

# Check container status
./docker-scripts.sh status

# Clean up temporary files
rm *.png
```

## Escalation
- If scraping structure changes, capture a small HTML excerpt in logs and add a targeted parser tweak. Avoid brittle assumptions; prefer tolerant regex + DOM traversal.

## Common Tasks for New Chats
- Start the app with Docker (above), then explore:
  - UI flows under `templates/` and `static/js/`
  - API behavior in `app/api/` and `API.md`
  - Business rules in `app/services/` (suggestions, validation)
  - Data shape in `app/models/` and stored JSON under `./data`

For deeper docs, read: `README.md`, `API.md`, `Project.md`, `CONTRIBUTING.md`, and `CHANGELOG.md`.
