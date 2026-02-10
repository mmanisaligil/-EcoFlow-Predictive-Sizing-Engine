"""Consumption profile, confidence, and demand band calculations."""
from __future__ import annotations


def build_consumption(
    user_daily_kwh: float,
    avg_kw: float | None,
    peak_kw: float | None,
    aggregated_daily_band: list[float],
    aggregated_peak_w_band: list[float],
    peak_multiplier_default: float,
) -> dict:
    effective_daily_kwh = max(user_daily_kwh, aggregated_daily_band[1])

    peak_inferred = False
    if peak_kw is not None:
        confidence = "HIGH"
        effective_peak_kw = peak_kw
        peak_band = [0.9 * effective_peak_kw, 1.0 * effective_peak_kw, 1.1 * effective_peak_kw]
    else:
        peak_inferred = True
        confidence = "LOW"
        inferred_source_kw = avg_kw if avg_kw is not None else (user_daily_kwh / 24.0)
        user_inferred_peak = inferred_source_kw * peak_multiplier_default
        effective_peak_kw = max(user_inferred_peak, aggregated_peak_w_band[1] / 1000.0)
        peak_band = [0.8 * effective_peak_kw, 1.0 * effective_peak_kw, 1.3 * effective_peak_kw]

    daily_band = [0.8 * effective_daily_kwh, 1.0 * effective_daily_kwh, 1.2 * effective_daily_kwh]

    return {
        "effective_daily_kwh": effective_daily_kwh,
        "effective_peak_kw": effective_peak_kw,
        "daily_kwh_band": daily_band,
        "peak_kw_band": peak_band,
        "peak_confidence": confidence,
        "peak_inferred": peak_inferred,
        "avg_kw_typical": effective_daily_kwh / 24.0,
    }
