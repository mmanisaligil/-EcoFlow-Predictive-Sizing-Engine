"""Family-specific hard constraints and feasibility checks."""
from __future__ import annotations


def evaluate_powerocean_constraints(phase: str, cls: str | None, required_modules: int, battery_unit_kwh: float, peak_kw: float) -> dict:
    warnings: list[str] = []
    feasible = True
    accessories: list[str] = []
    inverter: dict = {}

    if phase == "1P":
        inverter = {"phase": "1P", "class": None, "inverter_kw": 6.0, "count": 1, "parallel": False}
        max_batteries = 3
        if required_modules > max_batteries:
            feasible = False
            warnings.append("1P supports maximum 3 batteries (15 kWh nominal)")
        accessories = ["smart_meter_1p", "battery_base"]
    elif phase == "3P" and cls == "3P":
        inverter = {"phase": "3P", "class": "3P", "inverter_kw": 12.0, "count": 1, "parallel": False}
        max_jb = 3
        max_batteries = max_jb * 3
        jb_needed = (required_modules + 2) // 3
        if jb_needed > max_jb:
            feasible = False
            warnings.append("3P supports maximum 3 junction boxes and 9 batteries")
        accessories = ["junction_box", "smart_meter_3p", "battery_base"]
    elif phase == "3P" and cls == "3P_PLUS":
        inverter_count = 2 if peak_kw > 29.9 else 1
        inverter = {"phase": "3P", "class": "3P_PLUS", "inverter_kw": 29.9, "count": inverter_count, "parallel": inverter_count > 1}
        max_batteries = 12 * inverter_count
        max_total_battery_kwh = 120.0
        if required_modules > max_batteries:
            feasible = False
            warnings.append("3P_PLUS battery count exceeds JB limits")
        if required_modules * battery_unit_kwh > max_total_battery_kwh:
            feasible = False
            warnings.append("3P_PLUS total battery exceeds 120 kWh")
        if peak_kw > 59.8:
            feasible = False
            warnings.append("3P_PLUS max AC with 2 inverters is 59.8 kW")
        accessories = ["junction_box", "smart_meter_3p", "battery_base", "powerinsight_11"]
    else:
        raise ValueError("Invalid powerocean phase/class configuration")

    return {"feasible": feasible, "warnings": warnings, "accessories": accessories, "inverter": inverter}


def evaluate_stream_constraints(max_solar_kw: float, pv_kwp: float, required_modules: int) -> dict:
    warnings: list[str] = []
    feasible = True
    if max_solar_kw > 0 and pv_kwp > max_solar_kw:
        feasible = False
        warnings.append(f"PV {pv_kwp} kWp exceeds STREAM max_solar_kw {max_solar_kw} kW")
    if required_modules < 1:
        feasible = False
        warnings.append("STREAM needs at least one battery module")
    inverter = {"phase": "N/A", "class": "STREAM", "inverter_kw": None, "count": 1, "parallel": False}
    return {"feasible": feasible, "warnings": warnings, "accessories": ["wall_bracket"], "inverter": inverter}
