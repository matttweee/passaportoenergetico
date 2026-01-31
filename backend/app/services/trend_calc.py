"""User trend from two bills + position (green/yellow/red)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.config import get_settings


def monthlyize_days(days: float) -> float:
    if days <= 0:
        return 0.0
    return 30.0 / days


def compute_user_trend(
    recent: dict[str, Any],
    old: dict[str, Any],
) -> dict[str, Any]:
    """Build user_trend_json from two extracted bill dicts."""
    total_recent = (recent.get("total_due") or 0) or 0.0
    total_old = (old.get("total_due") or 0) or 0.0
    kwh_recent = (recent.get("kwh") or 0) or 0.0
    kwh_old = (old.get("kwh") or 0) or 0.0
    smc_recent = (recent.get("smc") or 0) or 0.0
    smc_old = (old.get("smc") or 0) or 0.0

    delta_total = total_recent - total_old
    delta_kwh = kwh_recent - kwh_old
    delta_smc = smc_recent - smc_old

    eur_per_kwh_recent = total_recent / kwh_recent if kwh_recent else None
    eur_per_kwh_old = total_old / kwh_old if kwh_old else None
    eur_per_kwh_delta = None
    if eur_per_kwh_recent is not None and eur_per_kwh_old is not None and eur_per_kwh_old != 0:
        eur_per_kwh_delta = (eur_per_kwh_recent - eur_per_kwh_old) / eur_per_kwh_old

    return {
        "total_recent": total_recent,
        "total_old": total_old,
        "delta_total": delta_total,
        "kwh_recent": kwh_recent,
        "kwh_old": kwh_old,
        "delta_kwh": delta_kwh,
        "smc_recent": smc_recent,
        "smc_old": smc_old,
        "delta_smc": delta_smc,
        "eur_per_kwh_recent": eur_per_kwh_recent,
        "eur_per_kwh_old": eur_per_kwh_old,
        "eur_per_kwh_delta_pct": eur_per_kwh_delta * 100 if eur_per_kwh_delta is not None else None,
    }


def compute_position(
    user_trend: dict[str, Any],
    zone_trend: dict[str, Any],
) -> tuple[str, str]:
    """Returns (position: green|yellow|red, explanation_short)."""
    settings = get_settings()
    green_pct = settings.TREND_GREEN_THRESHOLD_PCT
    yellow_pct = settings.TREND_YELLOW_THRESHOLD_PCT

    user_delta_pct = user_trend.get("eur_per_kwh_delta_pct")
    zone_delta_pct = zone_trend.get("eur_per_kwh_delta_pct") or 0.0

    if user_delta_pct is None:
        return "yellow", "Dati insufficienti per il confronto con la zona."

    diff_pct = abs((user_delta_pct or 0) - zone_delta_pct)

    if diff_pct <= green_pct:
        return "green", "Sei in linea con l'andamento della tua zona."
    if diff_pct <= yellow_pct:
        return "yellow", "Stai iniziando ad allontanarti dal trend della zona."
    return "red", "Il tuo andamento è fuori trend rispetto alla tua zona."
