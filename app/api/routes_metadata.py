from fastapi import APIRouter

from app.data.cache import get_data_cache

router = APIRouter(tags=["metadata"])

CONSTANTS = {
    "peak_multiplier_default": 4.0,
    "round_trip_efficiency": 0.92,
    "usable_fraction": 0.9,
    "night_fraction": 0.5,
    "direct_use_factor": 0.35,
    "storage_utilization_factor": 0.85,
    "annual_tariff_increase": 0.25,
    "carbon_factor": 0.42,
}


@router.get("/metadata")
def metadata() -> dict:
    cache = get_data_cache()
    templates = sorted(list(cache["expert_packs"].keys()))
    grouped: dict[str, list[str]] = {"AC1P": [], "AC3P": [], "DC12V": [], "DC24V": [], "DC48V": []}
    for template in templates:
        for pack in grouped:
            if template.startswith(pack):
                grouped[pack].append(template)
    return {
        "cities": sorted(list(cache["specific_yield"].keys())),
        "families": ["powerocean", "stream"],
        "constants": CONSTANTS,
        "powerocean_phase_options": ["1P", "3P"],
        "powerocean_3p_class_options": ["3P", "3P_PLUS"],
        "expert_load_templates": templates,
        "expert_load_templates_grouped": grouped,
    }
