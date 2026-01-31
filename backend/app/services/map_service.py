"""Map points: anonymized, gated by verification."""
from __future__ import annotations

import hashlib
import random
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import MapPoint, UserSession


GRID_SIZE = 0.01
JITTER = 0.002


def _jitter(lat: float, lng: float) -> tuple[float, float]:
    lat += random.uniform(-JITTER, JITTER)
    lng += random.uniform(-JITTER, JITTER)
    return round(lat, 5), round(lng, 5)


def _grid_round(lat: float, lng: float) -> tuple[float, float]:
    lat = round(lat / GRID_SIZE) * GRID_SIZE
    lng = round(lng / GRID_SIZE) * GRID_SIZE
    return lat, lng


def cap_to_approx_coords(cap: str) -> tuple[float, float]:
    """Rough CAP -> (lat, lng) for Italy. Fallback to center Italy."""
    defaults = {"00100": (41.9, 12.5), "20100": (45.46, 9.19), "80100": (40.84, 14.25)}
    cap = (cap or "00100").strip()[:5]
    if cap in defaults:
        return defaults[cap]
    try:
        prefix = int(cap[:3]) if len(cap) >= 3 else 0
        lat = 41.0 + (prefix % 10) * 0.5 + random.uniform(-0.2, 0.2)
        lng = 12.0 + (prefix % 7) * 0.5 + random.uniform(-0.2, 0.2)
        return _grid_round(lat, lng)
    except Exception:
        return (41.9, 12.5)


def add_map_point(db: Session, session_id: str, zone_key: str, position: str, cap: str) -> MapPoint:
    """Add anonymized point. session_id hashed."""
    lat, lng = cap_to_approx_coords(cap)
    lat, lng = _jitter(lat, lng)
    sid_hash = hashlib.sha256(session_id.encode()).hexdigest()[:16]
    point = MapPoint(
        zone_key=zone_key,
        approx_lat=lat,
        approx_lng=lng,
        color=position,
        source_session_id_hash=sid_hash,
    )
    db.add(point)
    db.commit()
    db.refresh(point)
    return point


def get_zone_points(db: Session, zone_key: str) -> list[dict[str, Any]]:
    """Points for zone (gated: only if zone has data). No identifiers."""
    rows = db.execute(
        select(MapPoint.approx_lat, MapPoint.approx_lng, MapPoint.color, MapPoint.created_at)
        .where(MapPoint.zone_key == zone_key)
        .order_by(MapPoint.created_at.desc())
        .limit(500)
    ).all()
    return [
        {"lat": r[0], "lng": r[1], "color": r[2], "created_at": r[3].isoformat() if r[3] else None}
        for r in rows
    ]


def coverage_opacity(count: int) -> float:
    """More points -> higher opacity (0.2 to 1.0)."""
    if count <= 0:
        return 0.2
    if count >= 50:
        return 1.0
    return 0.2 + 0.8 * (count / 50)
