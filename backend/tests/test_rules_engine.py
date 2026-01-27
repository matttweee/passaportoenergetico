from __future__ import annotations

from app.rules.engine import run_rules


def test_rules_missing_fields():
    extracted = {"latest": {"supplier": "Test"}, "older": None, "meta": {}}
    findings = run_rules(extracted)
    assert any(f.rule_id == "R_MISSING_FIELDS" for f in findings)


def test_total_sanity_flags_large_mismatch():
    extracted = {
        "latest": {
            "total_eur": 120.0,
            "fixed_fees": 10.0,
            "variable_eur": 10.0,
            "vat_eur": 2.0,
            "excise_eur": 1.0,
        },
        "older": None,
        "meta": {},
    }
    findings = run_rules(extracted)
    assert any(f.rule_id == "R_TOTAL_SANITY" and f.severity == "high" for f in findings)


def test_unit_cost_jump():
    extracted = {
        "latest": {"variable_eur": 80.0, "kwh": 200.0},
        "older": {"variable_eur": 40.0, "kwh": 200.0},
        "meta": {},
    }
    findings = run_rules(extracted)
    assert any(f.rule_id == "R_UNIT_COST_JUMP" for f in findings)

