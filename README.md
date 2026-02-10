# ecoflow-sizing-v13

Deterministic FastAPI + Next.js sizing platform for EcoFlow PowerOcean/STREAM recommendations.

> DigitalOcean single-container deployments use `GET /` as an embedded web UI served by FastAPI, so the app URL opens a usable interface instead of raw JSON.

## Assumption
To keep prototype speed high and deployment simple, the frontend is implemented with Next.js (web target) and calls the FastAPI engine over HTTP.

## Architecture
- `app/`: FastAPI backend and deterministic sizing domain engine
- `frontend/`: Apple-inspired Liquid Glass web UI (dashboard, inputs, analysis, export, component showcase)
- `datasets/`: JSON-only data inputs used by the engine

## Backend API
- `GET /` (browser UI with city/expert-load dropdowns, calculation-first flow, and optional XLSX export)
- `GET /health`
- `GET /metadata`
- `POST /analyze`
- `POST /export/xlsx`

## Frontend screens
- City dropdown populated from `/metadata`
- Expert load template multi-select from all packs
- Results/KPIs shown first; XLSX export unlocked after successful calculation
- Landing / Dashboard
- Manual Input Form + Expert Mode-ready layout
- Analysis Overview + KPI cards
- Recommendation cards for scenarios (S1/S2/S3)
- Solar vs load KPI bars
- Export/download controls
- Component showcase at `/showcase`

## Local run (Docker-first)
```bash
docker compose up --build
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## Backend-only local run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Frontend-only local run
```bash
cd frontend
npm install
npm run dev
```

## Design system notes
- System typography stack with Apple-first fonts
- Liquid Glass surfaces via blur + translucency + layered shadows
- Light/Dark mode adaptive tokens in `frontend/src/app/globals.css`
- Calm motion and high-contrast readable controls

## Environment
`.env.example` is included for backend defaults.

## Tests
```bash
pytest -q
```

## New usage notes (Scenario Selector + Expert Mode)
- **Scenario selector** (S1/S2/S3) now drives the selected BOM and economics directly; KPIs and BOM cards always reflect the selected scenario.
- **Scenario comparison** table shows capex/savings/payback for S1, S2, S3 side-by-side while keeping one selected scenario as primary.
- **Expert Mode** is OFF by default. Turn it on to:
  - pick working-hours level (`low`=0.6, `medium`=1.0, `high`=1.4)
  - search and multi-select templates grouped by source (AC1P, AC3P, DC12V, DC24V, DC48V)
  - send scaled expert-load contributions to the engine with auditable multiplier assumptions.
- **Technical details** moved to a user-friendly modal with Summary/Sizing/BOM/Economics/Raw JSON tabs and copy/download actions.
