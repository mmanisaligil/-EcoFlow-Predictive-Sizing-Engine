"""Dataset loaders with fail-fast validation for JSON inputs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"
PACK_FILES = ["packs-AC1P.json", "packs-AC3P.json", "packs-DC12V.json", "packs-DC24V.json", "packs-DC48V.json"]


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_specific_yield() -> dict[str, float]:
    raw = _load_json(DATASET_DIR / "SpecificYield_kWhkWp_Year.json")
    if not isinstance(raw, list):
        raise ValueError("SpecificYield_kWhkWp_Year.json must be a JSON array")
    out: dict[str, float] = {}
    for row in raw:
        if "Province" not in row or "SpecificYield" not in row:
            raise ValueError("SpecificYield_kWhkWp_Year.json rows require Province and SpecificYield")
        out[str(row["Province"])] = float(row["SpecificYield"])
    if not out:
        raise ValueError("SpecificYield_kWhkWp_Year.json has no valid rows")
    return out


def _norm_product(row: dict[str, Any]) -> dict[str, Any]:
    name = str(row.get("name") or row.get("Product") or "").strip()
    if not name:
        raise ValueError("Product entry missing name/Product")
    price = float(row.get("price_try") or row.get("Price (try VAT 20%)") or 0)
    inverter_kw = row.get("inverter_kw")
    if inverter_kw is None:
        inverter_kw = row.get("Power (kW)")
    battery_kwh = row.get("battery_kwh")
    if battery_kwh is None:
        battery_kwh = row.get("Capacity (kWh)")
    max_solar_kw = row.get("max_solar_kw")
    if max_solar_kw is None:
        max_solar_kw = row.get("Max. Solar (kW)")
    family = str(row.get("family") or ("stream" if "stream" in name.lower() else "powerocean")).lower()
    return {
        "product_id": str(row.get("product_id") or name.lower().replace(" ", "_")),
        "name": name,
        "family": family,
        "price_try": price,
        "inverter_kw": float(inverter_kw) if inverter_kw is not None else None,
        "battery_kwh": float(battery_kwh) if battery_kwh is not None else None,
        "max_solar_kw": float(max_solar_kw) if max_solar_kw is not None else None,
        "meta_tags": row.get("meta_tags") or [],
    }


def load_productlist() -> list[dict[str, Any]]:
    raw = _load_json(DATASET_DIR / "master_productlist.json")
    if not isinstance(raw, list):
        raise ValueError("master_productlist.json must be a JSON array")
    products = [_norm_product(r) for r in raw]
    for p in products:
        for c in ["product_id", "name", "family", "price_try", "inverter_kw", "battery_kwh", "max_solar_kw", "meta_tags"]:
            if c not in p:
                raise ValueError(f"master_productlist.json missing normalized column: {c}")
    return products


def load_expert_packs() -> dict[str, dict[str, list[float]]]:
    combined: dict[str, dict[str, list[float]]] = {}
    for filename in PACK_FILES:
        data = _load_json(DATASET_DIR / filename)
        if not isinstance(data, dict):
            raise ValueError(f"{filename} must be a JSON dictionary")
        for key, value in data.items():
            if "kwh_day" not in value or "peak_w" not in value:
                raise ValueError(f"{filename}:{key} requires kwh_day and peak_w")
            if len(value["kwh_day"]) != 3 or len(value["peak_w"]) != 3:
                raise ValueError(f"{filename}:{key} arrays must have [min,typ,max]")
            combined[key] = {"kwh_day": [float(x) for x in value["kwh_day"]], "peak_w": [float(x) for x in value["peak_w"]]}
    return combined


def load_accessories() -> dict[str, float]:
    raw = _load_json(DATASET_DIR / "accessories.json")
    if not isinstance(raw, dict):
        raise ValueError("accessories.json must be a JSON object")
    required = ["junction_box", "smart_meter_1p", "smart_meter_3p", "battery_base", "wall_bracket", "powerinsight_11"]
    for key in required:
        if key not in raw:
            raise ValueError(f"accessories.json missing key: {key}")
    return {k: float(v) for k, v in raw.items()}
