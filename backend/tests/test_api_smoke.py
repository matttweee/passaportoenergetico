from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _set_test_env(monkeypatch):
    # usa sqlite in-memory per smoke test
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("LOCAL_STORAGE_PATH", "/tmp/pe-tests")
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.setenv("ADMIN_PASSWORD", "test-admin")
    monkeypatch.setenv("SECRET_KEY", "test-secret")


def test_create_submission_and_status():
    from app.db.base import Base
    from app.db.session import get_engine, reset_engine_cache
    from app.main import create_app

    reset_engine_cache()
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    app = create_app()
    client = TestClient(app)

    r = client.post("/api/submissions", json={"email": "a@b.it", "phone": None, "consent": True, "expected_kinds": ["latest"]})
    assert r.status_code == 200
    submission_id = r.json()["id"]

    r2 = client.get(f"/api/submissions/{submission_id}/status")
    assert r2.status_code == 200
    assert r2.json()["analysis_state"] in ("pending", "running", "done", "error")


def test_admin_login_cookie():
    from app.db.base import Base
    from app.db.session import get_engine, reset_engine_cache
    from app.main import create_app

    reset_engine_cache()
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    app = create_app()
    client = TestClient(app)

    r = client.post("/api/admin/login", json={"password": "test-admin"})
    assert r.status_code == 200
    assert "pe_admin" in client.cookies

