# FLOWMIND — AI Traffic Intelligence

Phase-8 integrated prototype for AI-assisted traffic management: sensing, detection, prediction, signal optimization, route optimization, alerts, and impact metrics.

## Backend
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Health: `/api/health`
WebSocket: `/ws`

## Frontend
Open `frontend/index.html` in a browser. The frontend uses the production WebSocket endpoint when hosted over HTTPS and preserves a local development fallback.

## Validation
Phase-8 audit and deterministic demo scenario are included in `AUDIT_REPORT.md` and `demo_scenario.py`.
