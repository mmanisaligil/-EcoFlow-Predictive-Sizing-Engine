"""Expert load aggregation utilities."""
from __future__ import annotations


HOURS_MODE_MULTIPLIERS = {"low": 0.6, "medium": 1.0, "high": 1.4}


def aggregate_expert_loads(
    selected: list[str], packs: dict[str, dict[str, list[float]]], hours_mode: str = "medium"
) -> tuple[list[float], list[float], dict[str, dict[str, list[float]]], float]:
    if hours_mode not in HOURS_MODE_MULTIPLIERS:
        raise ValueError(f"Invalid expert_hours_mode: {hours_mode}")

    multiplier = HOURS_MODE_MULTIPLIERS[hours_mode]
    daily = [0.0, 0.0, 0.0]
    peak_w = [0.0, 0.0, 0.0]
    contributions: dict[str, dict[str, list[float]]] = {}

    for template_id in selected:
        if template_id not in packs:
            raise ValueError(f"Unknown expert load template: {template_id}")
        scaled_daily = [packs[template_id]["kwh_day"][i] * multiplier for i in range(3)]
        scaled_peak = [packs[template_id]["peak_w"][i] * multiplier for i in range(3)]
        contributions[template_id] = {
            "kwh_day_original": packs[template_id]["kwh_day"],
            "peak_w_original": packs[template_id]["peak_w"],
            "kwh_day_scaled": [round(v, 4) for v in scaled_daily],
            "peak_w_scaled": [round(v, 4) for v in scaled_peak],
        }
        for i in range(3):
            daily[i] += scaled_daily[i]
            peak_w[i] += scaled_peak[i]

    return daily, peak_w, contributions, multiplier
