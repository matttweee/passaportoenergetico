"""Zone aggregates (CAP-level) for trend comparison."""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models import TrendResult, UserSession

logger = logging.getLogger(__name__)


def get_zone_trend_json(db: Session, zone_key: str) -> dict[str, Any]:
    """Aggregate eur_per_kwh_delta_pct from TrendResults in same zone."""
    subq = (
        select(TrendResult.user_trend_json)
        .join(UserSession, UserSession.id == TrendResult.session_id)
        .where(UserSession.zone_key == zone_key)
        .where(TrendResult.user_trend_json.isnot(None))
    )
    rows = list(db.execute(subq).scalars().all())
    if not rows:
        return {"eur_per_kwh_delta_pct": 0.0, "count": 0}

    deltas = []
    for row in rows:
        uj = row[0] if row else None
        if uj is not None and isinstance(uj, dict) and uj.get("eur_per_kwh_delta_pct") is not None:
            deltas.append(uj["eur_per_kwh_delta_pct"])

    if not deltas:
        return {"eur_per_kwh_delta_pct": 0.0, "count": 0}

    deltas.sort()
    n = len(deltas)
    trimmed = deltas[n // 10 : 9 * n // 10] if n >= 10 else deltas
    median = trimmed[len(trimmed) // 2] if trimmed else 0.0
    return {"eur_per_kwh_delta_pct": median, "count": len(deltas)}


def cap_to_zone_key(cap: str) -> str:
    """CAP -> zone key (e.g. first 3 digits or full CAP)."""
    cap = (cap or "").strip()[:5]
    return cap or "unknown"
