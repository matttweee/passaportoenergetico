from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class RuleFinding:
    severity: str  # low|med|high
    title: str
    description: str
    estimated_impact_eur: float | None
    rule_id: str


FIXED_FEE_EUR_PER_30D_THRESHOLD = 40.0
TOTAL_MISMATCH_PCT = 0.02
UNIT_COST_JUMP_PCT = 0.25
USAGE_SPIKE_PCT = 0.30


def _get_num(d: dict[str, Any], key: str) -> float | None:
    v = d.get(key)
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        return None


def _period_days(d: dict[str, Any]) -> int | None:
    v = d.get("period_days")
    try:
        return int(v) if v is not None else None
    except Exception:
        return None


def rule_missing_fields(latest: dict[str, Any], older: dict[str, Any] | None) -> list[RuleFinding]:
    missing = []
    if _get_num(latest, "total_eur") is None:
        missing.append("totale (€)")
    if _get_num(latest, "kwh") is None and _get_num(latest, "mc") is None:
        missing.append("consumi (kWh/Smc)")
    if not missing:
        return []
    return [
        RuleFinding(
            severity="med",
            title="Dati chiave incompleti",
            description=f"Non sono stati individuati in modo affidabile: {', '.join(missing)}. La diagnosi resta indicativa.",
            estimated_impact_eur=None,
            rule_id="R_MISSING_FIELDS",
        )
    ]


def rule_total_sanity(latest: dict[str, Any], older: dict[str, Any] | None) -> list[RuleFinding]:
    total = _get_num(latest, "total_eur")
    if total is None:
        return []
    parts = {
        "fixed_fees": _get_num(latest, "fixed_fees"),
        "variable_eur": _get_num(latest, "variable_eur"),
        "vat_eur": _get_num(latest, "vat_eur"),
        "excise_eur": _get_num(latest, "excise_eur"),
    }
    present = {k: v for k, v in parts.items() if v is not None}
    if len(present) < 3:
        return []
    s = sum(present.values())
    diff = abs(s - total)
    if total > 0 and diff / total > TOTAL_MISMATCH_PCT:
        return [
            RuleFinding(
                severity="high",
                title="Totale non coerente con le componenti",
                description=f"Somma componenti ({s:.2f} €) diversa dal totale ({total:.2f} €) oltre il {int(TOTAL_MISMATCH_PCT*100)}%. Possibile voce mancante o errore di calcolo/lettura.",
                estimated_impact_eur=min(diff, total) * 0.25,
                rule_id="R_TOTAL_SANITY",
            )
        ]
    return []


def rule_fixed_fee_high(latest: dict[str, Any], older: dict[str, Any] | None) -> list[RuleFinding]:
    fixed = _get_num(latest, "fixed_fees")
    if fixed is None:
        return []
    days = _period_days(latest)
    if not days or days <= 0:
        return []
    fixed_30 = fixed / days * 30.0
    if fixed_30 > FIXED_FEE_EUR_PER_30D_THRESHOLD:
        sev = "high" if fixed_30 > FIXED_FEE_EUR_PER_30D_THRESHOLD * 1.5 else "med"
        impact = max(0.0, fixed_30 - FIXED_FEE_EUR_PER_30D_THRESHOLD) * 0.5
        return [
            RuleFinding(
                severity=sev,
                title="Quota fissa insolitamente alta",
                description=f"Quota fissa normalizzata ~{fixed_30:.2f} €/30gg (soglia {FIXED_FEE_EUR_PER_30D_THRESHOLD:.0f} €/30gg). Verifica voci fisse, potenza impegnata, oneri.",
                estimated_impact_eur=impact,
                rule_id="R_FIXED_FEE_HIGH",
            )
        ]
    return []


def rule_tax_sanity(latest: dict[str, Any], older: dict[str, Any] | None) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    total = _get_num(latest, "total_eur")
    vat = _get_num(latest, "vat_eur")
    excise = _get_num(latest, "excise_eur")

    if excise is not None and excise < 0:
        findings.append(
            RuleFinding(
                severity="med",
                title="Accisa negativa (anomalia)",
                description="È stata rilevata un'accisa negativa: può indicare un errore di lettura o una compensazione. Da verificare.",
                estimated_impact_eur=None,
                rule_id="R_TAX_SANITY",
            )
        )

    if total and vat is not None and total > 0 and vat >= 0:
        base = max(total - vat, 1.0)
        vat_pct = vat / base
        if vat_pct < 0.04 or vat_pct > 0.30:
            findings.append(
                RuleFinding(
                    severity="med",
                    title="IVA fuori range di buon senso",
                    description=f"Stima IVA ~{vat_pct*100:.1f}% (range atteso 4%–30%). Verificare aliquota e imponibile.",
                    estimated_impact_eur=None,
                    rule_id="R_TAX_SANITY",
                )
            )
    return findings


def _unit_cost(d: dict[str, Any]) -> float | None:
    var = _get_num(d, "variable_eur")
    qty = _get_num(d, "kwh") or _get_num(d, "mc")
    if var is None or qty is None or qty <= 0:
        return None
    return var / qty


def rule_unit_cost_jump(latest: dict[str, Any], older: dict[str, Any] | None) -> list[RuleFinding]:
    if not older:
        return []
    u_new = _unit_cost(latest)
    u_old = _unit_cost(older)
    if u_new is None or u_old is None or u_old <= 0:
        return []
    jump = (u_new - u_old) / u_old
    if jump > UNIT_COST_JUMP_PCT:
        return [
            RuleFinding(
                severity="med",
                title="Costo unitario variabile in aumento",
                description=f"Il costo variabile per unità è aumentato di ~{jump*100:.0f}% (da {u_old:.3f} a {u_new:.3f}). Controlla tariffa, fascia, offerte, indicizzazione.",
                estimated_impact_eur=None,
                rule_id="R_UNIT_COST_JUMP",
            )
        ]
    return []


def _usage_per_day(d: dict[str, Any]) -> float | None:
    qty = _get_num(d, "kwh") or _get_num(d, "mc")
    days = _period_days(d)
    if qty is None or not days or days <= 0:
        return None
    return qty / days


def rule_usage_spike(latest: dict[str, Any], older: dict[str, Any] | None) -> list[RuleFinding]:
    if not older:
        return []
    u_new = _usage_per_day(latest)
    u_old = _usage_per_day(older)
    if u_new is None or u_old is None or u_old <= 0:
        return []
    spike = (u_new - u_old) / u_old
    if spike > USAGE_SPIKE_PCT:
        return [
            RuleFinding(
                severity="med",
                title="Consumi in aumento rispetto alla bolletta precedente",
                description=f"Consumo medio giornaliero aumentato di ~{spike*100:.0f}% (da {u_old:.2f} a {u_new:.2f} per giorno). Valuta variazioni di uso, letture stimate/real, dispersioni.",
                estimated_impact_eur=None,
                rule_id="R_USAGE_SPIKE",
            )
        ]
    return []


RULES: list[Callable[[dict[str, Any], dict[str, Any] | None], list[RuleFinding]]] = [
    rule_missing_fields,
    rule_total_sanity,
    rule_fixed_fee_high,
    rule_unit_cost_jump,
    rule_usage_spike,
    rule_tax_sanity,
]

