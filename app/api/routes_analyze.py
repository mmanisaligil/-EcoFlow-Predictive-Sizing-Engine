from fastapi import APIRouter, HTTPException

from app.api.routes_metadata import CONSTANTS
from app.data.cache import get_data_cache
from app.domain.engine.consumption import build_consumption
from app.domain.engine.economics import calculate_co2, calculate_economics_for_capex, calculate_performance
from app.domain.engine.loads import aggregate_expert_loads
from app.domain.engine.sizing import size_system
from app.domain.engine.solar import build_solar_profile
from app.domain.models import AnalysisResponse, AnalyzeRequest

router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(payload: AnalyzeRequest) -> dict:
    cache = get_data_cache()

    try:
        hours_mode = payload.expert_hours_mode or "medium"
        selected_loads = payload.expert_loads if payload.expert_mode else []
        agg_daily_band, agg_peak_w_band, expert_contrib_by_template, hours_multiplier = aggregate_expert_loads(
            selected_loads, cache["expert_packs"], hours_mode=hours_mode
        )
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
            selected_scenario_id=payload.selected_scenario_id,
        )

        perf = calculate_performance(
            effective_daily_kwh=consumption["effective_daily_kwh"],
            daily_solar_avg=solar["daily_avg_kwh"],
            direct_use_factor=CONSTANTS["direct_use_factor"],
            storage_utilization_factor=CONSTANTS["storage_utilization_factor"],
        )

        econ_scenarios = {
            sid: calculate_economics_for_capex(
                effective_daily_kwh=consumption["effective_daily_kwh"],
                tariff=payload.tariff_tl_per_kwh,
                capex=sized["bom"]["scenarios"][sid]["capex_try"],
                offset_kwh=perf["offset_kwh_per_day_typical"],
                annual_tariff_increase=CONSTANTS["annual_tariff_increase"],
            )
            for sid in ["S1", "S2", "S3"]
        }
        econ_selected = econ_scenarios[payload.selected_scenario_id]
        co2 = calculate_co2(perf["offset_kwh_per_day_typical"], CONSTANTS["carbon_factor"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    warnings = list(sized["warnings"])
    if (
        econ_selected["payback_simple_years"] is not None
        and econ_selected["payback_simple_years"] > 30
        or econ_selected["annual_savings_try"] < 0.01 * econ_selected["capex_try"]
    ):
        warnings.append("System is oversized vs savings; ROI not meaningful. Consider smaller battery/PV increase.")

    assumptions = {
        **CONSTANTS,
        "solar_model_note": solar["disclaimer"],
        "self_consumption_model": "No export credit. Savings only from self-consumption.",
        "coverage_explanation": "Offset is constrained by demand and usable solar-to-storage throughput.",
        "expert_hours_mode": hours_mode if payload.expert_mode else None,
        "expert_hours_multiplier": hours_multiplier if payload.expert_mode else 1.0,
    }

    return {
        "inputs": {**payload.model_dump(), "city": solar["canonical_city"], "expert_loads": selected_loads},
        "assumptions": assumptions,
        "expert_load_contributions": {
            "aggregated_daily_kwh_band": [round(x, 4) for x in agg_daily_band],
            "aggregated_peak_kw_band": [round(x / 1000.0, 4) for x in agg_peak_w_band],
            "selected_templates": selected_loads,
            "hours_mode": hours_mode if payload.expert_mode else None,
            "multiplier": hours_multiplier if payload.expert_mode else 1.0,
            "templates": expert_contrib_by_template,
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
            "selected_scenario_id": payload.selected_scenario_id,
            "scenarios": sized["scenarios"],
            "inverter": sized["inverter"],
            "accessories": sized["accessories"],
        },
        "bom": sized["bom"],
        "performance": {
            **perf,
            "assumptions": {
                "direct_use_factor": CONSTANTS["direct_use_factor"],
                "storage_utilization_factor": CONSTANTS["storage_utilization_factor"],
                "explanation": "Offset is min(demand, storage-utilized solar); bounded for deterministic estimates.",
            },
        },
        "economics": {"selected": econ_selected, "scenarios": econ_scenarios},
        "co2": co2,
        "warnings": sorted(set(warnings)),
        "upgrade_paths": [],
    }
