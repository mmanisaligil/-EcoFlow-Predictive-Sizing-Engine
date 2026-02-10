"""Expert load aggregation utilities."""
from __future__ import annotations


def aggregate_expert_loads(selected: list[str], packs: dict[str, dict[str, list[float]]]) -> tuple[list[float], list[float]]:
    daily = [0.0, 0.0, 0.0]
    peak_w = [0.0, 0.0, 0.0]
    for template_id in selected:
        if template_id not in packs:
            raise ValueError(f"Unknown expert load template: {template_id}")
        for i in range(3):
            daily[i] += packs[template_id]["kwh_day"][i]
            peak_w[i] += packs[template_id]["peak_w"][i]
    return daily, peak_w
