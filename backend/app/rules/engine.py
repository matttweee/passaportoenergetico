from __future__ import annotations

from typing import Any

from app.rules.ruleset import RULES, RuleFinding


def run_rules(extracted_fields: dict[str, Any]) -> list[RuleFinding]:
    latest = (extracted_fields or {}).get("latest") or {}
    older = (extracted_fields or {}).get("older") or None
    findings: list[RuleFinding] = []
    for rule in RULES:
        findings.extend(rule(latest, older))
    # ordina high -> med -> low
    order = {"high": 0, "med": 1, "low": 2}
    findings.sort(key=lambda f: order.get(f.severity, 99))
    return findings

