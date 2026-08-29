"""
API integration tests.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.seed_db import seed
from app.safety_engine import DB_PATH


@pytest.fixture(autouse=True)
def ensure_db():
    if not DB_PATH.exists():
        seed(DB_PATH)


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_simulate_endpoint():
    resp = client.post("/simulate", json={"sql": "SELECT COUNT(*) FROM users;"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["original_database_protected"] is True
    assert data["risk_level"] == "low"


def test_simulate_delete():
    resp = client.post(
        "/simulate",
        json={"sql": "DELETE FROM users WHERE last_login < '2023-01-01';"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_level"] == "high"
    assert "users" in data["changed_tables"]


def test_approve():
    # First simulate to create an event
    sim = client.post("/simulate", json={"sql": "SELECT 1;"}).json()
    resp = client.post(
        "/approve",
        json={"simulation_id": sim["simulation_id"], "note": "Looks safe."},
    )
    assert resp.status_code == 200
    assert "did not execute" in resp.json()["message"].lower()


def test_reject():
    sim = client.post("/simulate", json={"sql": "DELETE FROM users;"}).json()
    resp = client.post(
        "/reject",
        json={"simulation_id": sim["simulation_id"], "note": "Too dangerous."},
    )
    assert resp.status_code == 200
    assert resp.json()["decision"] == "rejected"


def test_approve_missing_id():
    resp = client.post(
        "/approve",
        json={"simulation_id": "nonexistent-id", "note": "test"},
    )
    assert resp.status_code == 404


def test_audit():
    resp = client.get("/audit")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_examples():
    resp = client.get("/examples")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    assert "sql" in data[0]
