# FLOWMIND Build Plan

- [x] **Phase 0 (15 min)**: Audit + architecture (Repo creation, AGENTS.md, PLAN.md, AUDIT_REPORT.md). Roo Architect reviews.
- [x] **Phase 1**: Frontend working prototype (Cinematic landing + Dashboard). Works standalone with a built-in simulator.
- [x] **Phase 2**: `sim.py` + FastAPI (`/api/*` and `/ws`). Frontend swaps fake data for live data.
- [x] **Phase 3**: `signal_opt.py` (Fixed baseline, adaptive, Webster, optional RL).
- [x] **Phase 4**: `forecast.py`, `alerts.py`, and `impact.py`.
- [x] **Phase 5**: `router.py` alternate routes on a small city graph.
- [x] **Phase 6**: `detector.py` YOLO on a sample traffic video (Demo/Real mode).
- [x] **Phase 7**: Impact calculation, integration, tests, deployment readiness.