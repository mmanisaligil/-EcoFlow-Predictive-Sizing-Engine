# AGENTS.md — EcoFlow Predictive Sizing Engine (V1.2)

## Mission
Build and maintain a deterministic sizing calculator for EcoFlow Turkey use-cases that:
- accepts manual demand + PV + city + tariff inputs
- sizes either PowerOcean or STREAM systems (user-selected family)
- outputs B2B technical recommendations with explicit assumptions and constraints
- exports an auditable XLSX report
- deploys via Docker on DigitalOcean

This project is **engine-first**: Excel is an output format, not the source of truth.

---

## Scope (V1.2)
### Included
- Manual input sizing (no bill parsing)
- Family selection: PowerOcean OR STREAM
- PowerOcean: user must specify phase: 1P or 3P
- 3P requires class selection: 3P vs 3P_PLUS
- Battery sizing scenarios:
  - S1: 2 days outage
  - S2: 1 day outage
  - S3: night-only coverage
- No export credit: savings only from self-consumption
- FastAPI endpoints: /health, /metadata, /analyze, /export/xlsx

### Excluded
- OCR/PDF parsing (V2)
- Feed-in / export compensation
- Hourly simulation / seasonal time-series
- Full combinatorial optimizer across all SKUs (bounded selection rules only)

---

## Datasets
Place these files in `datasets/`:
- `SpecificYield_kWhkWp_Year.csv`
  - required columns: `city`, `kwh_per_kwp_year`
- `master_productlist.csv`
  - required columns: `product_id`, `name`, `family`, `price_try`, `inverter_kw`, `battery_kwh`, `max_solar_kw`, `meta_tags`
- `accessories_price_table.csv`
  - required columns: `accessory_id`, `name`, `price_try`

Startup must validate columns and fail with clear errors if missing.

---

## Engine Rules (non-negotiable)
### Demand bands
- daily_kwh_band = [0.8x, 1.0x, 1.2x]

### Peak kW inference
- If user provides peak_kw -> confidence HIGH, band [0.9x, 1.0x, 1.1x]
- Else infer from avg_kw or daily_kwh/24 -> confidence LOW, band [0.8x, 1.0x, 1.3x]
- Must output `peak_inferred=true` and assumptions text.

### Solar model
- annual_kwh = pv_kwp * yield(city)
- daily_avg = annual_kwh / 365
- Must label as annualized (winter may be lower).

### Battery scenarios
Let E_day = daily_kwh_typical.
Battery_nominal_required = Battery_usable_required / (round_trip_efficiency * usable_fraction)

- S1: Battery_usable_required = 2.0 * E_day
- S2: Battery_usable_required = 1.0 * E_day
- S3: Battery_usable_required = night_fraction * E_day

Map required nominal kWh to discrete modules from productlist.

### PowerOcean physical constraints
1P:
- max 3 batteries per inverter (15 kWh)
- inverter 6 kW
- no junction box, no parallel

3P (12 kW):
- junction box required
- 1 JB supports 3 batteries
- max 3 JB per inverter -> 9 batteries (45 kWh)
- no parallel
- inverter 12 kW

3P_PLUS (29.9 kW):
- junction box required
- 1 JB supports 3 batteries
- max 4 JB per inverter -> 12 batteries per inverter
- parallel supported up to 2 inverters
- max AC 59.8 kW total with 2 inverters
- max battery 120 kWh total
- engine may auto-select 1 vs 2 inverters only if needed for peak constraint

### No export credit
Savings are self-consumption only. Use conservative factors and always disclose them.

---

## API Contracts
- `GET /metadata`: return cities, families, options, constants defaults
- `POST /analyze`: compute full report JSON (auditable)
- `POST /export/xlsx`: produce an XLSX reflecting the analysis payload

---

## Testing
Minimum tests required:
- Demand inference produces LOW confidence when peak_kw missing
- PowerOcean constraints:
  - 1P rejects >3 batteries
  - 3P requires JB, enforces battery limits based on JB count
  - 3P_PLUS respects JB limits and optional 2-inverter parallel
- Scenario sizing outputs correct nominal kWh calculations

---

## Deployment
- Single Docker container.
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Add `/health` endpoint for DO health checks.
- No external API calls.

---

## Style & Guardrails
- Keep engine pure (no FastAPI dependencies inside domain engine).
- Every numeric output must be traceable to an assumption or an input.
- Prefer explicit warnings over optimistic estimates.
- If data is missing/invalid: fail fast with actionable error messages.
