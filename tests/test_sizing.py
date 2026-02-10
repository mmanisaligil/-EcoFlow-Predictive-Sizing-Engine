from app.domain.engine.consumption import build_consumption
from app.domain.engine.sizing import _scenario_nominal


def test_demand_inference_low_confidence_when_peak_missing() -> None:
    result = build_consumption(
        user_daily_kwh=20,
        avg_kw=None,
        peak_kw=None,
        aggregated_daily_band=[0, 0, 0],
        aggregated_peak_w_band=[0, 0, 0],
        peak_multiplier_default=1.8,
    )
    assert result["peak_confidence"] == "LOW"
    assert result["peak_inferred"] is True


def test_nominal_kwh_calculation_for_scenarios() -> None:
    e_day = 10.0
    rte = 0.9
    usable = 0.9
    night = 0.5
    assert round(_scenario_nominal(e_day, "S1", rte, usable, night), 3) == round(20 / (0.9 * 0.9), 3)
    assert round(_scenario_nominal(e_day, "S2", rte, usable, night), 3) == round(10 / (0.9 * 0.9), 3)
    assert round(_scenario_nominal(e_day, "S3", rte, usable, night), 3) == round(5 / (0.9 * 0.9), 3)
