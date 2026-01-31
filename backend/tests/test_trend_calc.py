"""Tests for trend calculation."""
from __future__ import annotations

import pytest
from app.services.trend_calc import compute_user_trend, compute_position


def test_compute_user_trend():
    recent = {"total_due": 100, "kwh": 200, "smc": 0}
    old = {"total_due": 80, "kwh": 180, "smc": 0}
    trend = compute_user_trend(recent, old)
    assert trend["delta_total"] == 20
    assert trend["delta_kwh"] == 20
    assert trend["eur_per_kwh_recent"] == 0.5
    assert trend["eur_per_kwh_old"] == pytest.approx(80 / 180)
    assert trend["eur_per_kwh_delta_pct"] is not None


def test_compute_position_green():
    user = {"eur_per_kwh_delta_pct": 5}
    zone = {"eur_per_kwh_delta_pct": 4}
    pos, msg = compute_position(user, zone)
    assert pos == "green"
    assert "in linea" in msg.lower()


def test_compute_position_red():
    user = {"eur_per_kwh_delta_pct": 50}
    zone = {"eur_per_kwh_delta_pct": 0}
    pos, msg = compute_position(user, zone)
    assert pos == "red"
    assert "fuori trend" in msg.lower()
