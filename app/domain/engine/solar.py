"""Solar generation model."""
from __future__ import annotations


def build_solar_profile(city: str, pv_kwp: float, specific_yield: dict[str, float]) -> dict:
    if city not in specific_yield:
        raise ValueError(f"City not found in yield dataset: {city}")
    yield_city = specific_yield[city]
    annual = pv_kwp * yield_city
    daily = annual / 365.0
    return {
        "yield_kwh_per_kwp_year": yield_city,
        "annual_kwh": annual,
        "daily_avg_kwh": daily,
        "disclaimer": "annualized average; winter lower",
    }
