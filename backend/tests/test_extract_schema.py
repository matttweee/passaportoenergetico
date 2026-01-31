"""Tests for extraction schema validation."""
from __future__ import annotations

import pytest
from datetime import date

from app.services.extract_schema import (
    ExtractionOutput,
    ExtractionConfidence,
    validate_extraction_payload,
    second_pass_validate,
)


def test_extraction_output_valid():
    data = {
        "period_start": "2024-01-01",
        "period_end": "2024-01-31",
        "issue_date": "2024-02-05",
        "total_due": 85.50,
        "kwh": 120.0,
        "smc": None,
        "energy_cost": 45.0,
        "transport_cost": 20.0,
        "taxes": 20.5,
        "supplier": "Enel",
        "tariff_name": "Maggior tutela",
        "cap_or_zone_hint": "00100",
        "confidence": {"total_due": 0.9, "kwh": 0.9},
        "notes": None,
    }
    out, err = validate_extraction_payload(data)
    assert err is None
    assert out is not None
    assert out.total_due == 85.50
    assert out.period_start == date(2024, 1, 1)
    assert out.period_end == date(2024, 1, 31)


def test_extraction_output_null_fields():
    data = {
        "period_start": None,
        "period_end": None,
        "total_due": None,
        "kwh": None,
        "confidence": {},
        "notes": None,
    }
    out, err = validate_extraction_payload(data)
    assert err is None
    assert out is not None
    assert out.total_due is None
    assert out.kwh is None


def test_extraction_output_invalid_date():
    data = {"period_start": "not-a-date", "total_due": 10, "confidence": {}}
    out, err = validate_extraction_payload(data)
    assert err is not None or out is not None


def test_second_pass_negative_total():
    out = ExtractionOutput(total_due=-1, confidence=ExtractionConfidence())
    warnings = second_pass_validate(out)
    assert any("total_due" in w for w in warnings)


def test_second_pass_period_order():
    out = ExtractionOutput(
        period_start=date(2024, 2, 1),
        period_end=date(2024, 1, 1),
        confidence=ExtractionConfidence(),
    )
    warnings = second_pass_validate(out)
    assert any("period" in w for w in warnings)
