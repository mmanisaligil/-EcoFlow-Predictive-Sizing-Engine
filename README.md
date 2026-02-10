# ecoflow-sizing-v13

Deterministic FastAPI + Next.js sizing platform for EcoFlow PowerOcean/STREAM recommendations.

## Assumption
To keep prototype speed high and deployment simple, the frontend is implemented with Next.js (web target) and calls the FastAPI engine over HTTP.

## Architecture
- `app/`: FastAPI backend and deterministic sizing domain engine
- `frontend/`: Apple-inspired Liquid Glass web UI (dashboard, inputs, analysis, export, component showcase)
- `datasets/`: JSON-only data inputs used by the engine

## Backend API
- `GET /` (default landing/status route for browser + platform checks)
- `GET /health`
- `GET /metadata`
- `POST /analyze`
- `POST /export/xlsx`

## Frontend screens
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
