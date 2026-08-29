# ProofGuard Frontend

React single-page app for ProofGuard.

## Setup

```bash
npm install
cp .env.example .env
```

## Run

```bash
npm run dev
```

Opens at http://localhost:5173

## Build

```bash
npm run build
```

## Configuration

Set `VITE_API_URL` in `.env` to point to the backend:

```
VITE_API_URL=http://127.0.0.1:8000
```

Default is `http://127.0.0.1:8000` if not set.
