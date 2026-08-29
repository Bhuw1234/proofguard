"""
Audit log for ProofGuard.

Stores simulation events and human decisions in a local SQLite database.
This is separate from the demo wallet.db to keep concerns apart.
"""

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_DB = Path(__file__).resolve().parent.parent / "data" / "audit.db"


def _get_conn() -> sqlite3.Connection:
    """Open (and optionally create) the audit database."""
    AUDIT_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(AUDIT_DB))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            proposed_sql TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            changed_tables TEXT,
            simulation_error TEXT,
            decision TEXT NOT NULL DEFAULT 'pending',
            note TEXT
        );
    """)
    conn.commit()
    return conn


def record_simulation(simulation_result: dict) -> str:
    """Save a simulation event. Returns the event ID."""
    conn = _get_conn()
    event_id = simulation_result.get("simulation_id", str(uuid.uuid4()))
    conn.execute(
        """INSERT OR REPLACE INTO events
           (id, timestamp, proposed_sql, risk_level, changed_tables, simulation_error, decision)
           VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
        (
            event_id,
            simulation_result.get("timestamp", datetime.now(timezone.utc).isoformat()),
            simulation_result.get("proposed_sql", ""),
            simulation_result.get("risk_level", "unknown"),
            ",".join(simulation_result.get("changed_tables", [])),
            simulation_result.get("simulation_error"),
        ),
    )
    conn.commit()
    conn.close()
    return event_id


def set_decision(simulation_id: str, decision: str, note: Optional[str] = None) -> bool:
    """
    Record a human decision (approved/rejected) for a simulation event.
    Returns True if the event was found and updated.
    """
    conn = _get_conn()
    cur = conn.execute(
        "UPDATE events SET decision = ?, note = ? WHERE id = ?",
        (decision, note, simulation_id),
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def get_recent(limit: int = 20) -> list[dict]:
    """Return recent audit events, newest first."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
