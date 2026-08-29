# ProofGuard Tool Contract

This document defines the MCP-style tool contract for ProofGuard's simulation endpoint.

## Primary Tool: simulate_database_action

**Purpose:** Simulate a SQL command against an isolated copy of the demo database and return a full impact analysis.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "sql": {
      "type": "string",
      "description": "A single SQL statement to simulate against the demo database"
    }
  },
  "required": ["sql"]
}
```

### Backend Endpoint

```
POST http://127.0.0.1:8000/simulate
Content-Type: application/json

{
  "sql": "DELETE FROM users WHERE last_login < '2023-01-01';"
}
```

### Output Schema

```json
{
  "simulation_id": "uuid",
  "proposed_sql": "string",
  "risk_level": "low | medium | high | critical",
  "original_database_protected": true,
  "execution_mode": "temporary SQLite clone",
  "before_counts": {
    "users": 10,
    "orders": 9,
    "payments": 9,
    "audit_logs": 3
  },
  "after_counts": {
    "users": 5,
    "orders": 9,
    "payments": 9,
    "audit_logs": 3
  },
  "changed": {
    "users": -5,
    "orders": 0,
    "payments": 0,
    "audit_logs": 0
  },
  "changed_tables": ["users"],
  "simulation_error": null,
  "dependency_warning": "Foreign key violations detected in: orders...",
  "safer_alternative": "-- Archive-first approach...",
  "timestamp": "ISO 8601 string"
}
```

### Error Cases

| Scenario | simulation_error value |
|----------|----------------------|
| Empty SQL | "SQL is empty." |
| Multiple statements | "Only one SQL statement is allowed per simulation." |
| Blocked command (PRAGMA, ATTACH, etc.) | "Blocked: 'PRAGMA' commands are not allowed in simulation." |
| Invalid SQL syntax | SQLite error message |
| Demo DB missing | "Demo database not found. Run: python -m app.seed_db" |

---

## Additional Tools

### get_audit_history

```
GET http://127.0.0.1:8000/audit
```

Returns a list of recent simulation events with decisions.

### approve_simulation

```
POST http://127.0.0.1:8000/approve
Content-Type: application/json

{
  "simulation_id": "uuid from simulation result",
  "note": "Optional human note"
}
```

Records approval. Does **not** execute SQL against the original database.

### reject_simulation

```
POST http://127.0.0.1:8000/reject
Content-Type: application/json

{
  "simulation_id": "uuid from simulation result",
  "note": "Optional human note"
}
```

Records rejection. Does **not** execute SQL against the original database.

### get_examples

```
GET http://127.0.0.1:8000/examples
```

Returns built-in demo SQL examples with descriptions.

---

## Safety Guarantees

1. The simulation tool **never** modifies the original `wallet.db`
2. SQL runs in a temporary file copy that is deleted after simulation
3. The approve/reject endpoints only record decisions — they don't execute SQL
4. Blocked commands (PRAGMA, ATTACH, DETACH, VACUUM, load_extension) are rejected before simulation
5. Only single SQL statements are allowed
