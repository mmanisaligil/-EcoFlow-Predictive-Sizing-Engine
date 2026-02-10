"""Scenario battery sizing and bill-of-material generation."""
from __future__ import annotations

from app.domain.engine.constraints import evaluate_powerocean_constraints, evaluate_stream_constraints


INVERTER_PRODUCT_IDS = {
    ("1P", None): "1p_6kw_inverter",
    ("3P", "3P"): "3p_12kw_inverter",
    ("3P", "3P_PLUS"): "3pp_29.9kw_inverter",
}


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


def _find_product_or_fail(products: list[dict], product_id: str, warning_msg: str) -> dict:
    for product in products:
        if product["product_id"] == product_id:
            return product
    raise ValueError(f"{warning_msg} Missing product_id={product_id} in datasets/master_productlist.json")


def _build_bom_for_scenario(
    family: str,
    scenario: dict,
    battery_product: dict,
    inverter_info: dict,
    accessories: list[str],
    accessories_price: dict[str, float],
    products: list[dict],
) -> dict:
    module_count = int(scenario["battery_modules"][0]["count"])
    items = [
        {
            "id": battery_product["product_id"],
            "name": battery_product["name"],
            "qty": module_count,
            "unit_price_try": battery_product["price_try"],
        }
    ]

    if family == "powerocean":
        key = (inverter_info["phase"], inverter_info.get("class"))
        product_id = INVERTER_PRODUCT_IDS.get(key)
        if not product_id:
            raise ValueError(f"Unsupported inverter mapping for phase/class: {key}")
        inverter_product = _find_product_or_fail(
            products,
            product_id,
            "Inverter product required for selected PowerOcean configuration was not found.",
        )
        items.append(
            {
                "id": inverter_product["product_id"],
                "name": inverter_product["name"],
                "qty": int(inverter_info["count"]),
                "unit_price_try": inverter_product["price_try"],
            }
        )

    for accessory_id in accessories:
        if accessory_id not in accessories_price:
            raise ValueError(f"Accessory pricing missing for {accessory_id}")
        items.append(
            {
                "id": accessory_id,
                "name": accessory_id.replace("_", " ").title(),
                "qty": 1,
                "unit_price_try": accessories_price[accessory_id],
            }
        )

    capex = sum(float(i["qty"]) * float(i["unit_price_try"]) for i in items)
    return {"items": items, "capex_try": round(capex, 2)}


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
    selected_scenario_id: str,
) -> dict:
    rte = assumptions["round_trip_efficiency"]
    usable_fraction = assumptions["usable_fraction"]
    night_fraction = assumptions["night_fraction"]

    battery_kwh, battery_product = _pick_battery_unit(products, family)
    scenarios: list[dict] = []
    warnings: list[str] = []
    scenario_boms: dict[str, dict] = {}

    inverter_info: dict | None = None
    accessory_names: list[str] = []

    for sid, sname in [("S1", "2_days_outage"), ("S2", "1_day_outage"), ("S3", "night_only_coverage")]:
        nominal_req = _scenario_nominal(e_day, sid, rte, usable_fraction, night_fraction)
        modules = int(-(-nominal_req // battery_kwh))
        if family == "powerocean":
            c = evaluate_powerocean_constraints(powerocean_phase or "", powerocean_3p_class, modules, battery_kwh, peak_kw)
        else:
            stream_items = [p for p in products if p["family"] == "stream"]
            max_solar_kw = max([float(p["max_solar_kw"] or 0.0) for p in stream_items], default=0.0)
            c = evaluate_stream_constraints(max_solar_kw=max_solar_kw, pv_kwp=pv_kwp, required_modules=modules)
        warnings.extend(c["warnings"])
        inverter_info = c["inverter"]
        accessory_names = c["accessories"]
        scenario = {
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
        scenarios.append(scenario)
        scenario_boms[sid] = _build_bom_for_scenario(
            family=family,
            scenario=scenario,
            battery_product=battery_product,
            inverter_info=inverter_info,
            accessories=accessory_names,
            accessories_price=accessories_price,
            products=products,
        )

    if selected_scenario_id not in scenario_boms:
        raise ValueError(f"Invalid selected_scenario_id: {selected_scenario_id}")

    return {
        "scenarios": scenarios,
        "inverter": inverter_info,
        "accessories": [{"id": a, "qty": 1, "price_try": accessories_price.get(a, 0.0)} for a in accessory_names],
        "bom": {
            "selected_scenario_id": selected_scenario_id,
            "selected": scenario_boms[selected_scenario_id],
            "scenarios": scenario_boms,
        },
        "warnings": sorted(set(warnings)),
    }
