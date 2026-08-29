# ProofGuard

**Test an AI agent's risky action safely before it touches the real system.**

ProofGuard is a safety layer for AI agents. You enter a risky SQL command, and ProofGuard:

1. Copies a fake SQLite database into a temporary sandbox
2. Runs the command only in that sandbox
3. Shows what would change (before/after row counts)
4. Explains the risk in plain English
5. Warns about foreign-key dependency issues
6. Suggests a safer alternative
7. Records the event in an audit log
8. Asks a human to approve or reject before anything else happens

The original database is never modified. This is called **counterfactual execution** — answering *"what would happen if we allowed this action?"*

---

## Why

AI coding agents and automation agents sometimes need to clean data, remove unused records, update a database, or delete old content. If they do this without checking consequences, they can break things.

ProofGuard lets you see the consequences before any real system is affected.

This MVP uses only fake local demo data. It never connects to a production database.

---

## Quick Example

**Input:**
```sql
DELETE FROM users WHERE last_login < '2023-01-01';
```

**Output (summary):**
- Risk level: **high**
- Users before: 10 → after: 5 (−5)
- Foreign key violations detected in: orders
- Dependency warning: Deleting these users would orphan dependent records
- Safer alternative: Archive users first, verify backups, then review

---

## Architecture

```
┌──────────────────────┐
│   React Frontend     │  (Vite, plain CSS)
│   localhost:5173      │
└──────────┬───────────┘
           │ HTTP (JSON)
           ▼
┌──────────────────────┐
│   FastAPI Backend     │  (Python, Uvicorn)
│   localhost:8000      │
│                      │
│  POST /simulate      │──► Safety Engine
│  POST /approve       │      │
│  POST /reject        │      ├─ Copy wallet.db → temp dir
│  GET  /audit         │      ├─ Run SQL in sandbox only
│  GET  /examples      │      ├─ Measure before/after
│  GET  /health        │      ├─ Check FK violations
│                      │      ├─ Suggest safer alternative
│  Audit Log (SQLite)  │      └─ Delete temp copy
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│   wallet.db (demo)   │  Never modified by simulation
│   audit.db (events)  │  Stores decisions
└──────────────────────┘
```

### Where TrueForge Fits

TrueForge is the agent harness for this project. See [docs/trueforge-setup.md](docs/trueforge-setup.md) for full details.

TrueForge is used for:
- **Agent orchestration** — the ProofGuard agent is defined as a TrueForge agent
- **Tool/MCP connection** — the `/simulate` endpoint is registered as an MCP-style tool
- **Session state** — TrueForge tracks the agent's session and conversation
- **Approval checkpoints** — the agent requires human approval before any action beyond simulation
- **Sandboxed execution workflow** — simulation results are inspectable in the tool output
- **Inspectable tool results** — all simulation details are returned as structured data

The agent prompt and tool contract are in the [trueforge/](trueforge/) directory.

---

## How the Sandbox Works

1. The safety engine copies `wallet.db` to a temporary directory
2. SQL runs against the copy only (foreign keys OFF for full impact measurement)
3. FK violations are checked separately via `PRAGMA foreign_key_check`
4. Row counts are measured before and after
5. The temporary copy is deleted after simulation
6. The original database is never opened for writes

---

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed_db
pytest -q
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

### TrueForge (Agent Harness)

```bash
npx @truefoundry/trueforge@latest
```

See [docs/trueforge-setup.md](docs/trueforge-setup.md) for agent and tool configuration.

---

## Running Tests

```bash
cd backend
source .venv/bin/activate
pytest -q
```

All tests use temporary databases where needed and never modify the demo `wallet.db`.

---

## Demo SQL Commands

| Command | Risk |
|---------|------|
| `DELETE FROM users WHERE last_login < '2023-01-01';` | high |
| `DELETE FROM audit_logs WHERE created_at < '2025-01-01';` | high |
| `SELECT * FROM users WHERE last_login < '2023-01-01';` | low |
| `DROP TABLE payments;` | critical |
| `UPDATE users SET email = 'x' WHERE id = 1;` | medium |

---

## Safety Limitations

- This is a hackathon MVP, not a production security system
- Only works with SQLite demo data
- Does not connect to real databases
- Risk classification is keyword-based (not semantic analysis)
- Only supports single SQL statements
- Does not handle all edge cases of SQL injection or obfuscation
- The "safer alternative" suggestions are illustrative and must be reviewed

---

## Deployment

See [docs/deployment.md](docs/deployment.md) for Vercel (frontend) and Render (backend) instructions.

Deployment has not been completed yet — the instructions explain what to do.

---

## Qodo Code Review Evidence

Representative merged pull request:

[PR #X — Add counterfactual SQL sandbox](REPLACE_WITH_REAL_MERGED_PR_LINK)

Qodo surfaced:

- REPLACE_WITH_A_REAL_QODO_FINDING

Action taken:

- REPLACE_WITH_THE_FIX_OR_JUSTIFIED_DISMISSAL

Follow-up review:

[View follow-up review](REPLACE_WITH_REAL_FOLLOW_UP_REVIEW_LINK)

---

## Demo Video

REPLACE_WITH_REAL_DEMO_VIDEO_LINK

A 3-minute recording script is in [DEMO.md](DEMO.md).

---

## Hackathon

This project is built for **The Agent Harness Hackathon** using TrueForge.

It demonstrates:
1. A real tool call (POST /simulate)
2. Sandboxed database execution (temporary SQLite copy)
3. A human approval checkpoint (approve/reject endpoints)
4. A clear audit history (GET /audit)
5. A simple UI (React single page)
6. TrueForge integration documentation
7. Qodo code review workflow

---

## License

MIT — see [LICENSE](LICENSE).
