# Architecture

## Overview

ProofGuard is a two-tier application:

- **Frontend** — React single-page app (Vite, plain CSS)
- **Backend** — Python FastAPI server with SQLite

There is no external database, no cloud service, and no authentication.

## Data Flow

```
User enters SQL in the UI
        │
        ▼
Frontend sends POST /simulate { sql: "..." }
        │
        ▼
Backend safety_engine.py:
  1. Validates SQL (non-empty, single statement, no blocked commands)
  2. Classifies risk (SELECT=low, DELETE=high, DROP=critical, etc.)
  3. Copies wallet.db → temp directory
  4. Runs SQL against the temp copy (FK enforcement OFF for full impact)
  5. Counts rows before and after
  6. Checks FK violations via PRAGMA foreign_key_check
  7. Generates dependency warning if violations found
  8. Suggests a safer alternative
  9. Deletes the temp copy
  10. Returns structured result
        │
        ▼
audit.py records the simulation event in audit.db
        │
        ▼
Frontend displays: risk level, impact table, warnings,
  safer alternative, and approve/reject panel
        │
        ▼
User clicks Approve or Reject
        │
        ▼
Frontend sends POST /approve or POST /reject
        │
        ▼
audit.py updates the event decision
  (no SQL is executed against wallet.db)
```

## Key Design Decisions

1. **File copy for isolation** — The demo database is never opened for writes by the simulation code. A temp copy is created, used, and deleted.

2. **FK enforcement OFF during simulation** — This lets the DELETE actually run in the sandbox so we can measure its full impact. FK violations are detected separately. This gives more useful output than just "FK constraint failed".

3. **Separate audit database** — Audit events are stored in `audit.db`, separate from the demo `wallet.db`. This keeps concerns apart and avoids accidentally mixing simulation data with demo data.

4. **Single-statement limit** — Only one SQL statement per simulation. This makes the safety analysis simpler and more reliable.

5. **No real AI model** — Risk classification is keyword-based. The "safer alternative" is template-based. This is intentional for a hackathon MVP — no LLM API calls needed.

## File Map

```
backend/
  app/
    main.py          → FastAPI routes and CORS config
    safety_engine.py → Sandbox simulation logic
    audit.py         → Audit event storage
    seed_db.py       → Creates demo wallet.db
  tests/
    conftest.py      → Test path setup
    test_safety_engine.py → Engine unit tests
    test_api.py      → API integration tests
  data/
    wallet.db        → Demo database (gitignored)
    audit.db         → Audit log (gitignored)

frontend/
  src/
    App.jsx          → Main UI component
    App.css          → Component styles
    api.js           → Backend API client
    main.jsx         → Entry point
    index.css        → Global styles
```
