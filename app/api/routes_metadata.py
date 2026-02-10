from fastapi import APIRouter

from app.data.cache import get_data_cache

router = APIRouter(tags=["metadata"])

CONSTANTS = {
    "peak_multiplier_default": 1.8,
    "round_trip_efficiency": 0.9,
    "usable_fraction": 0.9,
    "night_fraction": 0.5,
    "storage_utilization_factor": 0.85,
    "annual_tariff_increase": 0.2,
    "carbon_factor": 0.42,
}


@router.get("/metadata")
def metadata() -> dict:
    cache = get_data_cache()
    return {
        "cities": sorted(list(cache["specific_yield"].keys())),
        "families": ["powerocean", "stream"],
        "constants": CONSTANTS,
        "powerocean_phase_options": ["1P", "3P"],
        "powerocean_3p_class_options": ["3P", "3P_PLUS"],
        "expert_load_templates": sorted(list(cache["expert_packs"].keys())),
    }
