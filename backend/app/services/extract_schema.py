"""Strict Pydantic schema for bill extraction output."""
from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ExtractionConfidence(BaseModel):
    period_start: float = Field(ge=0, le=1, default=0)
    period_end: float = Field(ge=0, le=1, default=0)
    issue_date: float = Field(ge=0, le=1, default=0)
    total_due: float = Field(ge=0, le=1, default=0)
    kwh: float = Field(ge=0, le=1, default=0)
    smc: float = Field(ge=0, le=1, default=0)
    energy_cost: float = Field(ge=0, le=1, default=0)
    transport_cost: float = Field(ge=0, le=1, default=0)
    taxes: float = Field(ge=0, le=1, default=0)
    supplier: float = Field(ge=0, le=1, default=0)
    tariff_name: float = Field(ge=0, le=1, default=0)
    cap_or_zone_hint: float = Field(ge=0, le=1, default=0)


class ExtractionOutput(BaseModel):
    period_start: date | None = None
    period_end: date | None = None
    issue_date: date | None = None
    total_due: float | None = None
    kwh: float | None = None
    smc: float | None = None
    energy_cost: float | None = None
    transport_cost: float | None = None
    taxes: float | None = None
    supplier: str | None = None
    tariff_name: str | None = None
    cap_or_zone_hint: str | None = None
    confidence: ExtractionConfidence = Field(default_factory=ExtractionConfidence)
    notes: str | None = None

    @field_validator("total_due", "kwh", "smc", "energy_cost", "transport_cost", "taxes", mode="before")
    @classmethod
    def coerce_float(cls, v: Any) -> float | None:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            v = v.replace(",", ".").strip()
            if not v:
                return None
            try:
                return float(v)
            except ValueError:
                return None
        return None

    @field_validator("period_start", "period_end", "issue_date", mode="before")
    @classmethod
    def coerce_date(cls, v: Any) -> date | None:
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            v = v.strip()[:10]
            if len(v) == 10:
                try:
                    return date.fromisoformat(v)
                except ValueError:
                    pass
        return None


def validate_extraction_payload(data: dict[str, Any]) -> tuple[ExtractionOutput | None, str | None]:
    """Validate raw extraction dict. Returns (ExtractionOutput, error_message)."""
    try:
        out = ExtractionOutput.model_validate(data)
        return out, None
    except Exception as e:
        return None, str(e)


def second_pass_validate(out: ExtractionOutput) -> list[str]:
    """Second-pass: totals >= 0, dates consistent. Returns list of warnings."""
    warnings: list[str] = []
    for name, val in [
        ("total_due", out.total_due),
        ("kwh", out.kwh),
        ("smc", out.smc),
        ("energy_cost", out.energy_cost),
        ("transport_cost", out.transport_cost),
        ("taxes", out.taxes),
    ]:
        if val is not None and val < 0:
            warnings.append(f"{name} cannot be negative")
    if out.period_start and out.period_end and out.period_start > out.period_end:
        warnings.append("period_start must be <= period_end")
    return warnings
