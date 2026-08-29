# TrueForge Setup

This document explains how ProofGuard integrates with TrueForge as the agent harness.

## What TrueForge Does in ProofGuard

TrueForge is used as the orchestration layer for the ProofGuard agent:

| Role | How it's used |
|------|---------------|
| Agent orchestration | The ProofGuard agent is defined with a system prompt that enforces safety rules |
| Tool/MCP connection | The `/simulate` endpoint is registered as an MCP-style tool |
| Session state | TrueForge tracks the conversation and simulation context |
| Approval checkpoints | The agent instructs users to approve/reject before any next step |
| Sandboxed execution | Simulation results show exactly what would change in isolation |
| Inspectable tool results | All simulation data is returned as structured JSON |

## Prerequisites

- Node.js 18+
- The ProofGuard backend running on `http://127.0.0.1:8000`

## Setup Steps

### 1. Start TrueForge

```bash
npx @truefoundry/trueforge@latest
```

This opens the TrueForge UI in your browser.

### 2. Create the ProofGuard Agent

In the TrueForge UI:

1. Create a new agent
2. Name: **ProofGuard Orchestrator**
3. Paste the system prompt from [trueforge/agent-prompt.md](../trueforge/agent-prompt.md)

### 3. Add the Simulation Tool

In the TrueForge UI, add an MCP-style tool:

1. Tool name: `simulate_database_action`
2. Description: "Simulate a SQL command against an isolated copy of the demo database. Returns risk level, impact analysis, dependency warnings, and a safer alternative."
3. Input schema:
   ```json
   {
     "type": "object",
     "properties": {
       "sql": {
         "type": "string",
         "description": "The SQL statement to simulate"
       }
     },
     "required": ["sql"]
   }
   ```
4. Backend endpoint: `POST http://127.0.0.1:8000/simulate`
5. The tool sends `{ "sql": "<user input>" }` and returns the full simulation result

### 4. Add Additional Tools (Optional)

You can also register these endpoints as tools:

| Tool | Endpoint | Method | Description |
|------|----------|--------|-------------|
| `get_audit_history` | `/audit` | GET | View recent simulation events and decisions |
| `approve_simulation` | `/approve` | POST | Record human approval for a simulation |
| `reject_simulation` | `/reject` | POST | Record human rejection for a simulation |

### 5. Test the Agent

1. In the TrueForge chat, type:
   ```
   What would happen if I ran: DELETE FROM users WHERE last_login < '2023-01-01';
   ```
2. The agent should call the `simulate_database_action` tool
3. It should explain the results and ask for your approval

## Important Notes

- TrueForge tool connections must be configured manually in the TrueForge UI
- This repository does not automatically configure your TrueForge account
- The agent prompt and tool contract are templates — adjust them based on TrueForge's current UI and API
- Make sure the backend is running before testing the agent

## Verifying the Integration

After setup, you should see:

1. The agent calls the simulation tool when given SQL
2. The tool returns structured results (risk level, impact, warnings)
3. The agent explains results in plain language
4. The agent asks for human approval
5. All interactions appear in the TrueForge session history

## Troubleshooting

- **Tool not connecting:** Check that the backend is running on port 8000
- **CORS errors:** The backend allows `localhost:5173` by default. If TrueForge runs on a different port, add it to the `FRONTEND_ORIGIN` env var or the CORS origins list in `main.py`
- **Agent not calling tools:** Check that the tool schema matches what TrueForge expects. Different TrueForge versions may have slightly different MCP configurations.
