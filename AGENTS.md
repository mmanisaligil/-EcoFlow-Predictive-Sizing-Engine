# AGENTS.md — EcoFlow Predictive Sizing Engine (V1.3)

## Mission
Build and maintain a deterministic sizing calculator for EcoFlow Turkey use-cases that:
- accepts manual demand + PV + city + tariff inputs
- sizes either PowerOcean or STREAM systems (user-selected family)
- outputs B2B technical recommendations with explicit assumptions and constraints
- exports an auditable XLSX report
- deploys via Docker on DigitalOcean

This project is **engine-first**: Excel is an output format, not the source of truth.

## V1.3 dataset rule
Use JSON datasets under `datasets/` only. No CSV parsing.

## Guardrails
- Keep engine pure (no FastAPI imports in domain engine)
- Every numeric output must map to an assumption or input
- Fail fast with actionable validation messages
- No external API calls
