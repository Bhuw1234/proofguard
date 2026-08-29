"""
Safety engine for ProofGuard.

Core idea: copy the demo database to a temp directory, run the proposed SQL
only against that copy, measure the impact, and throw the copy away.

The original database is never opened for writes by this module.
"""

import sqlite3
import shutil
import tempfile
import uuid
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "wallet.db"

TRACKED_TABLES = ["users", "orders", "payments", "audit_logs"]

# SQLite admin commands that should never run in simulation
BLOCKED_PATTERNS = [
    r"\bPRAGMA\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bVACUUM\b",
    r"\bload_extension\b",
]


def classify_risk(sql: str) -> str:
    """Classify risk based on the SQL operation keyword."""
    upper = sql.strip().upper()
    if upper.startswith("SELECT"):
        return "low"
    if upper.startswith("INSERT"):
        return "low"
    if upper.startswith("UPDATE"):
        return "medium"
    if upper.startswith("DELETE"):
        return "high"
    if upper.startswith("DROP"):
        return "critical"
    if upper.startswith("ALTER"):
        return "critical"
    # Anything we can't identify is treated as high risk
    return "high"


def _check_blocked(sql: str) -> Optional[str]:
    """Return a rejection reason if the SQL contains a blocked command."""
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            return f"Blocked: '{pattern.strip(chr(92)).strip('b')}' commands are not allowed in simulation."
    return None


def _count_rows(conn: sqlite3.Connection) -> dict:
    """Count rows in each tracked table."""
    counts = {}
    for table in TRACKED_TABLES:
        try:
            row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            counts[table] = row[0]
        except sqlite3.OperationalError:
            counts[table] = None
    return counts


def _detect_dependency_warning(sql: str, conn: sqlite3.Connection, before: dict, after: dict) -> Optional[str]:
    """
    Warn if the operation would orphan child rows.
    Checks both row-count changes and actual FK violations in the sandbox.
    """
    upper = sql.strip().upper()
    if not upper.startswith("DELETE"):
        return None

    # Check for actual FK violations after the (no-FK) execution
    try:
        violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
        if violations:
            tables_affected = set(row[0] for row in violations)
            return (
                f"Foreign key violations detected in: {', '.join(tables_affected)}. "
                f"Deleting these rows would orphan dependent records. "
                f"Consider archiving instead of deleting."
            )
    except Exception:
        pass

    if "USERS" in upper:
        users_removed = (before.get("users") or 0) - (after.get("users") or 0)
        if users_removed > 0:
            return (
                f"Removing {users_removed} user(s) may orphan rows in 'orders' and 'payments'. "
                f"Orders and payments reference users via foreign keys. "
                f"Consider archiving users instead of deleting them."
            )

    if "ORDERS" in upper:
        orders_removed = (before.get("orders") or 0) - (after.get("orders") or 0)
        if orders_removed > 0:
            return (
                f"Removing {orders_removed} order(s) may orphan rows in 'payments'. "
                f"Payments reference orders via foreign keys."
            )

    return None


from app.ai_analyzer import generate_safer_alternative_with_ai

def _suggest_safer_alternative(sql: str, risk_level: str, changed_tables: list, simulation_error: str) -> Optional[str]:
    """Suggest a safer SQL approach for destructive operations using AI or fallback."""
    upper = sql.strip().upper()
    
    # Do not suggest alternatives for safe commands
    if upper.startswith("SELECT") or upper.startswith("INSERT"):
        return None

    # Hardcoded exact rule for the hackathon demo (must override AI)
    if upper.startswith("DELETE") and "USERS" in upper:
        where_match = re.search(r"WHERE\s+(.+?);\s*$", sql, re.IGNORECASE | re.DOTALL)
        where_clause = where_match.group(1) if where_match else "/* your condition here */"
        return (
            "BEGIN;\n\n"
            "CREATE TABLE IF NOT EXISTS archived_users AS\n"
            "SELECT * FROM users WHERE 0;\n\n"
            "INSERT INTO archived_users\n"
            "SELECT *\n"
            "FROM users\n"
            f"WHERE {where_clause};\n\n"
            "COMMIT;\n\n"
            "-- No DELETE is performed in this recommended workflow.\n"
            "-- Keep original users because orders and payments may still reference them.\n"
            "-- Verify retention policy, backup restore, and dependency handling before\n"
            "-- any production deletion."
        )

    # Try AI generation for other queries
    ai_suggestion = generate_safer_alternative_with_ai(sql, risk_level, changed_tables, simulation_error)
    if ai_suggestion:
        return f"{ai_suggestion}\n\n-- This is an illustrative safer option and must be reviewed before production use."

    # Fallback rules
    if upper.startswith("DELETE"):
        return (
            "-- General safer approach:\n"
            "-- 1. Back up the table before deleting.\n"
            "-- 2. Run in a staging environment first.\n"
            "-- 3. Check foreign-key dependencies.\n"
            "-- 4. Wrap in a transaction so you can rollback.\n"
            "-- 5. Get human approval before proceeding."
        )

    if upper.startswith("DROP"):
        return (
            "-- Safer approach:\n"
            "-- 1. Export table data before dropping.\n"
            "-- 2. Use ALTER TABLE RENAME instead of DROP if restructuring.\n"
            "-- 3. Test in staging first.\n"
            "-- 4. Prepare a rollback script."
        )

    if upper.startswith("UPDATE"):
        return (
            "-- Safer approach:\n"
            "-- 1. SELECT the rows first to verify your WHERE clause.\n"
            "-- 2. Back up before bulk updates.\n"
            "-- 3. Use a transaction.\n"
            "-- 4. Limit the update to a small batch first."
        )

    return None


def simulate(sql: str) -> dict:
    """
    Run proposed SQL in an isolated temporary copy of the demo database.

    The original wallet.db is never modified. The temporary copy is
    deleted after simulation completes.
    """
    simulation_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    sql = sql.strip()

    # --- Basic validation ---
    if not sql:
        return {
            "simulation_id": simulation_id,
            "proposed_sql": sql,
            "risk_level": "unknown",
            "original_database_protected": True,
            "execution_mode": "temporary SQLite clone",
            "simulation_error": "SQL is empty.",
            "timestamp": timestamp,
        }

    # Only one statement allowed
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    if len(statements) > 1:
        return {
            "simulation_id": simulation_id,
            "proposed_sql": sql,
            "risk_level": "unknown",
            "original_database_protected": True,
            "execution_mode": "temporary SQLite clone",
            "simulation_error": "Only one SQL statement is allowed per simulation.",
            "timestamp": timestamp,
        }

    # Check for blocked admin commands
    blocked_reason = _check_blocked(sql)
    if blocked_reason:
        return {
            "simulation_id": simulation_id,
            "proposed_sql": sql,
            "risk_level": "critical",
            "original_database_protected": True,
            "execution_mode": "temporary SQLite clone",
            "simulation_error": blocked_reason,
            "timestamp": timestamp,
        }

    risk_level = classify_risk(sql)

    if not DB_PATH.exists():
        return {
            "simulation_id": simulation_id,
            "proposed_sql": sql,
            "risk_level": risk_level,
            "original_database_protected": True,
            "execution_mode": "temporary SQLite clone",
            "simulation_error": "Demo database not found. Run: python -m app.seed_db",
            "timestamp": timestamp,
        }

    # --- Use a file copy so destructive SQL never reaches the demo database ---
    tmp_dir = tempfile.mkdtemp(prefix="proofguard_")
    tmp_db = Path(tmp_dir) / "wallet_sandbox.db"

    try:
        shutil.copy2(str(DB_PATH), str(tmp_db))

        # FK enforcement is OFF during execution so the SQL runs fully and
        # we can measure actual impact. We check FK violations separately.
        conn = sqlite3.connect(str(tmp_db))

        before_counts = _count_rows(conn)

        simulation_error = None
        try:
            conn.execute("BEGIN;")
            conn.execute(sql)
            conn.execute("COMMIT;")
        except Exception as e:
            simulation_error = str(e)
            try:
                conn.execute("ROLLBACK;")
            except Exception:
                pass

        after_counts = _count_rows(conn)

        # Calculate changes
        changed = {}
        changed_tables = []
        for table in TRACKED_TABLES:
            b = before_counts.get(table, 0) or 0
            a = after_counts.get(table, 0) or 0
            diff = a - b
            changed[table] = diff
            if diff != 0:
                changed_tables.append(table)

        dependency_warning = _detect_dependency_warning(sql, conn, before_counts, after_counts)
        safer_alternative = _suggest_safer_alternative(sql, risk_level, changed_tables, simulation_error)

        conn.close()

        return {
            "simulation_id": simulation_id,
            "proposed_sql": sql,
            "risk_level": risk_level,
            "original_database_protected": True,
            "execution_mode": "temporary SQLite clone",
            "before_counts": before_counts,
            "after_counts": after_counts,
            "changed": changed,
            "changed_tables": changed_tables,
            "simulation_error": simulation_error,
            "dependency_warning": dependency_warning,
            "safer_alternative": safer_alternative,
            "timestamp": timestamp,
        }

    finally:
        # Clean up temp copy — it was only for simulation
        shutil.rmtree(tmp_dir, ignore_errors=True)
