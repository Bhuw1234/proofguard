# Demo Guide

A step-by-step guide for recording a 3-minute demo of ProofGuard.

## Startup

### Terminal 1 — Backend

```bash
cd backend
source .venv/bin/activate
python -m app.seed_db
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

---

## Demo Script (~3 minutes)

### 1. Introduce (30 seconds)

"ProofGuard is a safety layer for AI agents. Before an agent runs a dangerous database command, ProofGuard simulates it in an isolated sandbox and shows what would happen."

### 2. Show the dangerous delete (60 seconds)

1. Click **"Dangerous user cleanup"** example button
2. SQL fills in: `DELETE FROM users WHERE last_login < '2023-01-01';`
3. Click **"Run safe simulation"**
4. Point out:
   - Risk level: **high**
   - Original database protected: ✓
   - Timeline showing the agent workflow
   - Impact table: users went from 10 to 5 (−5)
   - FK violation warning: orders table has orphaned records
   - Safer alternative: archive-first approach

### 3. Reject the action (15 seconds)

1. Type a note: "Too dangerous, use archive approach instead"
2. Click **"Reject"**
3. Show the rejection is recorded in the audit history

### 4. Try a safe query (30 seconds)

1. Click **"Archive inactive users (safe)"** example
2. Click **"Run safe simulation"**
3. Point out: risk level is **low**, no rows changed

### 5. Prove the original database is unchanged (30 seconds)

Run in a terminal:

```bash
sqlite3 backend/data/wallet.db "SELECT COUNT(*) FROM users;"
sqlite3 backend/data/wallet.db "SELECT COUNT(*) FROM orders;"
sqlite3 backend/data/wallet.db "SELECT COUNT(*) FROM payments;"
```

Expected output:
```
10
9
9
```

"All counts match the original seed data. The simulation never touched it."

### 6. Wrap up (15 seconds)

"ProofGuard uses TrueForge as the agent harness. The simulation endpoint is an MCP-style tool that any TrueForge agent can call. The human approval checkpoint ensures no destructive action is taken without review."

---

## Additional Commands to Try

```sql
-- Critical risk
DROP TABLE payments;

-- Medium risk
UPDATE users SET email = 'deleted@example.com' WHERE id = 1;

-- Blocked command
PRAGMA table_info(users);

-- Invalid SQL (safe error)
DELEET FORM users;

-- Multiple statements (rejected)
DELETE FROM users; DROP TABLE orders;
```

---

## Verification Commands

After any number of simulations, run these to confirm the original database is unchanged:

```bash
sqlite3 backend/data/wallet.db "SELECT COUNT(*) FROM users;"
# Expected: 10

sqlite3 backend/data/wallet.db "SELECT COUNT(*) FROM orders;"
# Expected: 9

sqlite3 backend/data/wallet.db "SELECT COUNT(*) FROM payments;"
# Expected: 9
```
