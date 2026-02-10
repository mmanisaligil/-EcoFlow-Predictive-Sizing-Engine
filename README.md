# ecoflow-sizing-v13

Deterministic FastAPI sizing engine for EcoFlow PowerOcean/STREAM recommendations.

## Scope
- Manual inputs only (no bill parsing, no OCR)
- JSON datasets only from `datasets/`
- PowerOcean and STREAM family sizing with bounded constraints
- Auditable JSON analysis and XLSX export
- Dockerized for DigitalOcean deployment

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker
```bash
docker compose up --build
```

## API
- `GET /health`
- `GET /metadata`
- `POST /analyze`
- `POST /export/xlsx`

## Deterministic assumptions
Defaults are exposed via `/metadata`:
- `peak_multiplier_default`
- `round_trip_efficiency`
- `usable_fraction`
- `night_fraction`
- `storage_utilization_factor`
- `annual_tariff_increase`
- `carbon_factor`

## Datasets
Loaded from JSON:
- `SpecificYield_kWhkWp_Year.json`
- `master_productlist.json`
- `packs-*.json`
- `accessories.json`

Engine fails fast on missing files/invalid schema.

## Tests
```bash
pytest -q
```
