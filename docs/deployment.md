# Deployment

ProofGuard has two parts to deploy: the frontend (static site) and the backend (Python API).

Deployment has **not** been completed yet. These are instructions for when you're ready.

---

## Frontend → Vercel

1. Push your code to GitHub.
2. Go to [vercel.com](https://vercel.com) and import the repository.
3. Set the **root directory** to `frontend`.
4. Vercel should auto-detect Vite. Framework preset: Vite.
5. Build command: `npm run build`
6. Output directory: `dist`
7. Add an environment variable:
   - `VITE_API_URL` = your backend URL (e.g. `https://proofguard-api.onrender.com`)
8. Deploy.
9. **Important:** After setting the environment variable, trigger a redeploy so Vite bakes the value into the build.

---

## Backend → Render or Railway

### Render

1. Go to [render.com](https://render.com) and create a new **Web Service**.
2. Connect your GitHub repository.
3. Set the **root directory** to `backend`.
4. Build command:
   ```
   pip install -r requirements.txt && python -m app.seed_db
   ```
5. Start command:
   ```
   ./start.sh
   ```
6. Add an environment variable:
   - `FRONTEND_ORIGIN` = your Vercel frontend URL (e.g. `https://proofguard.vercel.app`)
7. Deploy.

### Railway

Similar steps — set root to `backend`, same build and start commands, same environment variable.

---

## After Deployment

1. Visit your Vercel URL and test a simulation.
2. Verify the backend health check: `curl https://your-backend-url/health`
3. Run a test simulation and confirm the response comes back.

---

## Notes

- The demo database `wallet.db` is created during the build step (`python -m app.seed_db`).
- The audit database `audit.db` is created automatically on first use.
- Both `.db` files live in `backend/data/` and are ephemeral on free-tier hosting (they reset on redeploy).
- This is fine for a hackathon demo. For persistent data, you'd use a managed database.
