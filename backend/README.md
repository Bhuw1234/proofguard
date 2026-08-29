# ProofGuard Backend

FastAPI backend for counterfactual SQL simulation.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed_db
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
pytest -q
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /simulate | Run SQL in sandbox |
| POST | /approve | Record approval decision |
| POST | /reject | Record rejection decision |
| GET | /audit | Recent audit events |
| GET | /examples | Demo SQL examples |
