"""
ProofGuard API — FastAPI backend.

Provides endpoints for counterfactual SQL simulation,
human approval/rejection, and audit history.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from app.safety_engine import simulate
from app.audit import record_simulation, set_decision, get_recent

# --- CORS ---
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

app = FastAPI(
    title="ProofGuard",
    description="Counterfactual safety layer for AI agents",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/response models ---

class SimulateRequest(BaseModel):
    sql: str


class DecisionRequest(BaseModel):
    simulation_id: str
    note: Optional[str] = None


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "ok", "service": "proofguard"}


@app.post("/simulate")
def run_simulation(req: SimulateRequest):
    """Run proposed SQL in an isolated sandbox and return impact analysis."""
    result = simulate(req.sql)
    record_simulation(result)
    return result


@app.post("/approve")
def approve(req: DecisionRequest):
    """
    Record human approval for a simulation.
    This does NOT execute SQL against the original database.
    """
    found = set_decision(req.simulation_id, "approved", req.note)
    if not found:
        raise HTTPException(status_code=404, detail="Simulation event not found.")
    return {
        "message": "Approval recorded. ProofGuard did not execute SQL against the original database.",
        "simulation_id": req.simulation_id,
        "decision": "approved",
    }


@app.post("/reject")
def reject(req: DecisionRequest):
    """
    Record human rejection for a simulation.
    This does NOT execute SQL against the original database.
    """
    found = set_decision(req.simulation_id, "rejected", req.note)
    if not found:
        raise HTTPException(status_code=404, detail="Simulation event not found.")
    return {
        "message": "Rejection recorded. No SQL was executed against the original database.",
        "simulation_id": req.simulation_id,
        "decision": "rejected",
    }


@app.get("/audit")
def audit():
    """Return recent audit events."""
    return get_recent()


@app.get("/examples")
def examples():
    """Return built-in demo SQL examples."""
    return [
        {
            "label": "Dangerous user cleanup",
            "sql": "DELETE FROM users WHERE last_login < '2023-01-01';",
            "description": "Deletes users who haven't logged in since 2023. Risky because orders and payments depend on these users.",
        },
        {
            "label": "Audit-log cleanup",
            "sql": "DELETE FROM audit_logs WHERE created_at < '2025-01-01';",
            "description": "Removes old audit log entries. Lower risk but still destructive.",
        },
        {
            "label": "Archive inactive users (safe)",
            "sql": "SELECT * FROM users WHERE last_login < '2023-01-01';",
            "description": "Preview which users would be affected. This is a read-only operation.",
        },
    ]
