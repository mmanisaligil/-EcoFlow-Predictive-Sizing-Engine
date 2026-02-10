"""Performance, economics and carbon calculations."""
from __future__ import annotations


def calculate_performance(
    effective_daily_kwh: float,
    daily_solar_avg: float,
    direct_use_factor: float,
    storage_utilization_factor: float,
) -> dict:
    direct_use = daily_solar_avg * direct_use_factor
    storage_use = daily_solar_avg * storage_utilization_factor
    offset = min(effective_daily_kwh, storage_use, max(0.0, direct_use + storage_use))
    coverage_ratio = (offset / effective_daily_kwh) if effective_daily_kwh else 0.0
    self_consumption_ratio = (offset / daily_solar_avg) if daily_solar_avg else 0.0
    return {
        "coverage_ratio_typical": round(coverage_ratio, 4),
        "self_consumption_ratio_typical": round(self_consumption_ratio, 4),
        "offset_kwh_per_day_typical": round(offset, 3),
    }


def calculate_economics_for_capex(
    effective_daily_kwh: float,
    tariff: float,
    capex: float,
    offset_kwh: float,
    annual_tariff_increase: float,
) -> dict:
    annual_bill = effective_daily_kwh * tariff * 365
    annual_savings = offset_kwh * tariff * 365
    simple = (capex / annual_savings) if annual_savings > 0 else None
    adjusted = None
    if annual_savings > 0:
        inflated_savings = annual_savings * (1 + annual_tariff_increase)
        adjusted = capex / inflated_savings
    return {
        "annual_bill_try_est": round(annual_bill, 2),
        "annual_savings_try": round(annual_savings, 2),
        "payback_simple_years": round(simple, 2) if simple is not None else None,
        "payback_inflation_adjusted_years": round(adjusted, 2) if adjusted is not None else None,
        "capex_try": round(capex, 2),
    }


def calculate_co2(offset_kwh: float, carbon_factor: float) -> dict:
    return {
        "carbon_factor": carbon_factor,
        "co2_saved_kg_per_year": round(offset_kwh * 365 * carbon_factor, 2),
    }
