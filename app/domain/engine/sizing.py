"""Scenario battery sizing and bill-of-material generation."""
from __future__ import annotations

from app.domain.engine.constraints import evaluate_powerocean_constraints, evaluate_stream_constraints


def _pick_battery_unit(products: list[dict], family: str) -> tuple[float, dict]:
    candidates = [p for p in products if p["family"] == family and p["battery_kwh"]]
    if not candidates:
        candidates = [p for p in products if p["battery_kwh"]]
    if not candidates:
        raise ValueError("No battery products available in product list")
    selected = sorted(candidates, key=lambda x: x["battery_kwh"])[0]
    return float(selected["battery_kwh"]), selected


def _scenario_nominal(e_day: float, scenario_id: str, rte: float, usable_fraction: float, night_fraction: float) -> float:
    usable_req = {"S1": 2.0 * e_day, "S2": 1.0 * e_day, "S3": night_fraction * e_day}[scenario_id]
    return usable_req / (rte * usable_fraction)


def size_system(
    family: str,
    e_day: float,
    peak_kw: float,
    pv_kwp: float,
    products: list[dict],
    accessories_price: dict[str, float],
    assumptions: dict,
    powerocean_phase: str | None,
    powerocean_3p_class: str | None,
) -> dict:
    rte = assumptions["round_trip_efficiency"]
    usable_fraction = assumptions["usable_fraction"]
    night_fraction = assumptions["night_fraction"]

    battery_kwh, battery_product = _pick_battery_unit(products, family)
    scenarios: list[dict] = []
    warnings: list[str] = []

    inverter_info: dict | None = None
    accessory_names: list[str] = []

    for sid, sname in [("S1", "2_days_outage"), ("S2", "1_day_outage"), ("S3", "night_only_coverage")]:
        nominal_req = _scenario_nominal(e_day, sid, rte, usable_fraction, night_fraction)
        modules = int(-(-nominal_req // battery_kwh))  # ceil positive floats
        if family == "powerocean":
            c = evaluate_powerocean_constraints(powerocean_phase or "", powerocean_3p_class, modules, battery_kwh, peak_kw)
        else:
            stream_items = [p for p in products if p["family"] == "stream"]
            max_solar_kw = max([float(p["max_solar_kw"] or 0.0) for p in stream_items], default=0.0)
            c = evaluate_stream_constraints(max_solar_kw=max_solar_kw, pv_kwp=pv_kwp, required_modules=modules)
        warnings.extend(c["warnings"])
        inverter_info = c["inverter"]
        accessory_names = c["accessories"]
        scenarios.append(
            {
                "id": sid,
                "name": sname,
                "battery_nominal_kwh_required": round(nominal_req, 3),
                "battery_modules": [
                    {
                        "product_id": battery_product["product_id"],
                        "name": battery_product["name"],
                        "module_kwh": battery_kwh,
                        "count": modules,
                    }
                ],
                "feasible": c["feasible"],
                "notes": c["warnings"] or ["Within bounded deterministic constraints"],
            }
        )

    # BOM built from S2 (typical) scenario
    s2_modules = scenarios[1]["battery_modules"][0]["count"]
    battery_cost = s2_modules * battery_product["price_try"]
    accessory_items = [{"id": a, "qty": 1, "price_try": accessories_price.get(a, 0.0)} for a in accessory_names]
    accessory_cost = sum(i["qty"] * i["price_try"] for i in accessory_items)
    capex = battery_cost + accessory_cost

    return {
        "scenarios": scenarios,
        "inverter": inverter_info,
        "accessories": accessory_items,
        "bom": {
            "items": [
                {"id": battery_product["product_id"], "name": battery_product["name"], "qty": s2_modules, "unit_price_try": battery_product["price_try"]}
            ]
            + accessory_items,
            "capex_try": round(capex, 2),
        },
        "warnings": sorted(set(warnings)),
    }
