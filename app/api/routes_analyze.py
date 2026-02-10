from fastapi import APIRouter, HTTPException

from app.api.routes_metadata import CONSTANTS
from app.data.cache import get_data_cache
from app.domain.engine.consumption import build_consumption
from app.domain.engine.economics import calculate_co2, calculate_economics, calculate_performance
from app.domain.engine.loads import aggregate_expert_loads
from app.domain.engine.sizing import size_system
from app.domain.engine.solar import build_solar_profile
from app.domain.models import AnalysisResponse, AnalyzeRequest

router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(payload: AnalyzeRequest) -> dict:
    cache = get_data_cache()

    try:
        agg_daily_band, agg_peak_w_band = aggregate_expert_loads(payload.expert_loads, cache["expert_packs"])
        consumption = build_consumption(
            user_daily_kwh=payload.daily_kwh,
            avg_kw=payload.avg_kw,
            peak_kw=payload.peak_kw,
            aggregated_daily_band=agg_daily_band,
            aggregated_peak_w_band=agg_peak_w_band,
            peak_multiplier_default=CONSTANTS["peak_multiplier_default"],
        )
        solar = build_solar_profile(payload.city, payload.pv_kwp, cache["specific_yield"])
        sized = size_system(
            family=payload.system_family,
            e_day=consumption["effective_daily_kwh"],
            peak_kw=consumption["effective_peak_kw"],
            pv_kwp=payload.pv_kwp,
            products=cache["products"],
            accessories_price=cache["accessories"],
            assumptions=CONSTANTS,
            powerocean_phase=payload.powerocean_phase,
            powerocean_3p_class=payload.powerocean_3p_class,
        )

        perf = calculate_performance(
            effective_daily_kwh=consumption["effective_daily_kwh"],
            daily_solar_avg=solar["daily_avg_kwh"],
            storage_utilization_factor=CONSTANTS["storage_utilization_factor"],
        )
        econ = calculate_economics(
            effective_daily_kwh=consumption["effective_daily_kwh"],
            tariff=payload.tariff_tl_per_kwh,
            capex=sized["bom"]["capex_try"],
            offset_kwh=perf["offset_kwh_per_day_typical"],
            annual_tariff_increase=CONSTANTS["annual_tariff_increase"],
        )
        co2 = calculate_co2(perf["offset_kwh_per_day_typical"], CONSTANTS["carbon_factor"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    assumptions = {
        **CONSTANTS,
        "solar_model_note": solar["disclaimer"],
        "self_consumption_model": "No export credit. Savings only from self-consumption.",
    }

    return {
        "inputs": payload.model_dump(),
        "assumptions": assumptions,
        "expert_load_contributions": {
            "aggregated_daily_kwh_band": agg_daily_band,
            "aggregated_peak_kw_band": [x / 1000.0 for x in agg_peak_w_band],
            "selected_templates": payload.expert_loads,
        },
        "confidence": {"peak_kw": consumption["peak_confidence"], "peak_inferred": consumption["peak_inferred"]},
        "profiles": {
            "consumption": {
                "daily_kwh_band": consumption["daily_kwh_band"],
                "peak_kw_band": consumption["peak_kw_band"],
                "avg_kw_typical": consumption["avg_kw_typical"],
            },
            "solar": {
                "yield_kwh_per_kwp_year": solar["yield_kwh_per_kwp_year"],
                "annual_kwh": solar["annual_kwh"],
                "daily_avg_kwh": solar["daily_avg_kwh"],
            },
        },
        "sizing": {
            "scenarios": sized["scenarios"],
            "inverter": sized["inverter"],
            "accessories": sized["accessories"],
        },
        "bom": sized["bom"],
        "performance": perf,
        "economics": econ,
        "co2": co2,
        "warnings": sized["warnings"],
        "upgrade_paths": [],
    }
