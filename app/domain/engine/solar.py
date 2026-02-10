"""Solar generation model."""
from __future__ import annotations

from unicodedata import normalize


CITY_ALIAS_OVERRIDES = {
    "Ýstanbul": "İstanbul",
    "Istanbul": "İstanbul",
    "Istambul": "İstanbul",
    "Adiyaman": "Adıyaman",
    "Agri": "Ağrı",
    "Aydin": "Aydın",
    "Balikesir": "Balıkesir",
    "Bartin": "Bartın",
}


def normalize_city_input(city: str, specific_yield: dict[str, float]) -> str:
    raw = city.strip()
    if raw in specific_yield:
        return raw
    if raw in CITY_ALIAS_OVERRIDES and CITY_ALIAS_OVERRIDES[raw] in specific_yield:
        return CITY_ALIAS_OVERRIDES[raw]

    folded_raw = normalize("NFKD", raw).replace("ı", "i").replace("İ", "I")
    folded_raw = "".join(ch for ch in folded_raw if ord(ch) < 128).lower()
    for key in specific_yield:
        folded_key = normalize("NFKD", key).replace("ı", "i").replace("İ", "I")
        folded_key = "".join(ch for ch in folded_key if ord(ch) < 128).lower()
        if folded_key == folded_raw:
            return key

    raise ValueError(f"City not found in yield dataset: {city}")


def build_solar_profile(city: str, pv_kwp: float, specific_yield: dict[str, float]) -> dict:
    canonical_city = normalize_city_input(city, specific_yield)
    yield_city = specific_yield[canonical_city]
    annual = pv_kwp * yield_city
    daily = annual / 365.0
    return {
        "canonical_city": canonical_city,
        "yield_kwh_per_kwp_year": yield_city,
        "annual_kwh": annual,
        "daily_avg_kwh": daily,
        "disclaimer": "annualized average; winter lower",
    }
