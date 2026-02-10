"""Pydantic models for request and response contracts."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class AnalyzeRequest(BaseModel):
    system_family: Literal["powerocean", "stream"]
    city: str
    pv_kwp: float = Field(ge=0)
    tariff_tl_per_kwh: float = Field(gt=0)
    daily_kwh: float = Field(gt=0)
    avg_kw: float | None = Field(default=None, ge=0)
    peak_kw: float | None = Field(default=None, ge=0)
    powerocean_phase: Literal["1P", "3P"] | None = None
    powerocean_3p_class: Literal["3P", "3P_PLUS"] | None = None
    selected_scenario_id: Literal["S1", "S2", "S3"] = "S3"
    expert_mode: bool = False
    expert_hours_mode: Literal["low", "medium", "high"] | None = None
    expert_loads: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_powerocean_fields(self) -> "AnalyzeRequest":
        if self.system_family == "powerocean" and self.powerocean_phase is None:
            raise ValueError("powerocean_phase is required when system_family is powerocean")
        if self.system_family != "powerocean" and (self.powerocean_phase or self.powerocean_3p_class):
            raise ValueError("powerocean_phase and powerocean_3p_class must be null for stream")
        if self.system_family == "powerocean" and self.powerocean_phase == "3P" and self.powerocean_3p_class is None:
            raise ValueError("powerocean_3p_class is required when powerocean_phase is 3P")
        if self.system_family == "powerocean" and self.powerocean_phase == "1P" and self.powerocean_3p_class is not None:
            raise ValueError("powerocean_3p_class must be null for 1P")
        if not self.expert_mode and self.expert_loads:
            self.expert_loads = []
        if self.expert_mode and self.expert_hours_mode is None:
            self.expert_hours_mode = "medium"
        return self


class HealthResponse(BaseModel):
    status: str = "ok"


class MetadataResponse(BaseModel):
    cities: list[str]
    families: list[str]
    constants: dict[str, float]
    powerocean_phase_options: list[str]
    powerocean_3p_class_options: list[str]
    expert_load_templates: list[str]


class AnalysisResponse(BaseModel):
    inputs: dict[str, Any]
    assumptions: dict[str, Any]
    expert_load_contributions: dict[str, Any]
    confidence: dict[str, Any]
    profiles: dict[str, Any]
    sizing: dict[str, Any]
    bom: dict[str, Any]
    performance: dict[str, Any]
    economics: dict[str, Any]
    co2: dict[str, Any]
    warnings: list[str]
    upgrade_paths: list[dict[str, Any]]
