## Chat Onboarding: Contract Tracker

Use this one-pager to quickly learn how this project runs, how to start/stop it with Docker, and how the application is structured.
Look through README.md for an overview of the Project.
Keep the CHAT_LEARN.md up-to-date to onboard new chats quickly. Keep concise.

### What this app is
- **Purpose**: Track contractor working days, validate constraints, and forecast earnings.
- **Stack**: Python Flask backend with HTML/JS frontend. Packaged and run via **Docker/Docker Compose**.
- **Data**: JSON files persisted under `./data` (mounted as a Docker volume).

### Run the app (Docker)
Recommended path is the helper script `docker-scripts.sh`.

```bash
# From repo root
./docker-scripts.sh build   # Build image (contract-tracker:latest)
./docker-scripts.sh run     # Run container (port 5000, ./data volume)

# Status / logs / stop / cleanup
./docker-scripts.sh status
./docker-scripts.sh logs
./docker-scripts.sh stop
./docker-scripts.sh cleanup
```

Access the web UI at `http://localhost:5000`.

### Run with Docker Compose
```bash
docker-compose up -d                   # App + data volume
docker-compose --profile with-nginx up -d  # With nginx reverse proxy
```

Notes:
- The script auto-creates `./data` for persistence.
- Environment variables like `FLASK_ENV` and `SECRET_KEY` are set in the container (see `docker-scripts.sh`). For production, configure securely and prefer `Dockerfile.prod`/compose profiles.

### API quick reference
- Base URL (dev): `http://localhost:5000/api`
- Core endpoints: `GET/POST /api/contracts/`, `GET/PUT/DELETE /api/contracts/{key}`
- Day ops: `POST /api/contracts/{key}/days`, suggestions `GET/POST /api/contracts/{key}/suggestions`, validate `GET /api/contracts/{key}/validate`
- Dashboard/settings: `GET /api/dashboard/`, `GET/PUT /api/dashboard/settings`
See `API.md` for request/response details.

### Application structure
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

### Common tasks for new chats
- Start the app with Docker (above), then explore:
  - UI flows under `templates/` and `static/js/`
  - API behavior in `app/api/` and `API.md`
  - Business rules in `app/services/` (suggestions, validation)
  - Data shape in `app/models/` and stored JSON under `./data`

### Local (non-Docker) dev (optional)
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Testing with the Chrome agent
- Start the app (Docker or local), then use the Chrome agent to:
  - Navigate to `http://localhost:5000` and exercise UI flows
  - Capture snapshots/screenshots and read console/network logs
  - Run performance traces and analyze Core Web Vitals
- This is useful for automated/regression checks of pages like `dashboard`, `contracts`, and `settings`.

### Git workflow (docs-first)
Always update relevant docs alongside code changes, then commit:
```bash
git add -A
git commit -m "docs: update CHAT_LEARN and related docs; feat/fix: <short summary>"
git push origin <your-branch>
```
Prefer conventional commit prefixes (e.g., `feat:`, `fix:`, `docs:`, `refactor:`) and keep `README.md`/`API.md` in sync with behavior changes.

### Conventions
- Keep data sanitized and validated across layers (see `app/utils/sanitization.py` and validation services).
- Prefer Docker workflows for parity; use Compose profiles for nginx.
- Submit changes with clear descriptions and keep API/README updated.
- You rebuild container, run the new code, and then Test your changes have been successful. Look for any issues that may have introduced bugs. If found, fix them. Keep the Application in running, working order.

For deeper docs, read: `README.md`, `API.md`, `Project.md`, `CONTRIBUTING.md`, and `CHANGELOG.md`.


