"""
Tests for the safety engine.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from app.seed_db import seed
from app.safety_engine import simulate, classify_risk, DB_PATH


@pytest.fixture(autouse=True)
def ensure_db():
    """Make sure the demo database exists before each test."""
    if not DB_PATH.exists():
        seed(DB_PATH)


class TestSeedDatabase:
    def test_tables_exist(self):
        conn = sqlite3.connect(str(DB_PATH))
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        conn.close()
        assert "users" in tables
        assert "orders" in tables
        assert "payments" in tables
        assert "audit_logs" in tables

    def test_expected_data(self):
        conn = sqlite3.connect(str(DB_PATH))
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        payments = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
        conn.close()
        assert users == 10
        assert orders == 9
        assert payments == 9


class TestClassifyRisk:
    def test_select_is_low(self):
        assert classify_risk("SELECT * FROM users;") == "low"

    def test_insert_is_low(self):
        assert classify_risk("INSERT INTO users VALUES (1,'a','b','c');") == "low"

    def test_update_is_medium(self):
        assert classify_risk("UPDATE users SET name='x';") == "medium"

    def test_delete_is_high(self):
        assert classify_risk("DELETE FROM users;") == "high"

    def test_drop_is_critical(self):
        assert classify_risk("DROP TABLE users;") == "critical"

    def test_alter_is_critical(self):
        assert classify_risk("ALTER TABLE users ADD COLUMN x TEXT;") == "critical"


class TestSimulation:
    def test_destructive_does_not_change_original(self):
        conn = sqlite3.connect(str(DB_PATH))
        before = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()

        simulate("DELETE FROM users WHERE last_login < '2023-01-01';")

        conn = sqlite3.connect(str(DB_PATH))
        after = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()

        assert before == after, "Original database was modified!"

    def test_delete_shows_impact(self):
        result = simulate("DELETE FROM users WHERE last_login < '2023-01-01';")
        assert result["risk_level"] == "high"
        assert result["original_database_protected"] is True
        assert result["before_counts"]["users"] > result["after_counts"]["users"]

    def test_pragma_blocked(self):
        result = simulate("PRAGMA table_info(users);")
        assert result["simulation_error"] is not None
        assert "Blocked" in result["simulation_error"]

    def test_attach_blocked(self):
        result = simulate("ATTACH DATABASE ':memory:' AS mem;")
        assert result["simulation_error"] is not None

    def test_empty_sql(self):
        result = simulate("")
        assert result["simulation_error"] == "SQL is empty."

    def test_multiple_statements_rejected(self):
        result = simulate("DELETE FROM users; DROP TABLE orders;")
        assert "one SQL statement" in result["simulation_error"]

    def test_invalid_sql_returns_error(self):
        result = simulate("DELEET FORM users;")
        assert result["simulation_error"] is not None

    def test_select_is_safe(self):
        result = simulate("SELECT * FROM users;")
        assert result["risk_level"] == "low"
        assert result["simulation_error"] is None

    def test_dependency_warning(self):
        result = simulate("DELETE FROM users WHERE last_login < '2023-01-01';")
        assert result["dependency_warning"] is not None
        assert "orphan" in result["dependency_warning"].lower()

def test_safer_alternative_user_deletion():
    from app.safety_engine import simulate
    result = simulate("DELETE FROM users WHERE last_login < '2023-01-01';")
    alt = result["safer_alternative"]
    assert "INSERT INTO archived_users" in alt
    assert "DELETE FROM users" not in alt
