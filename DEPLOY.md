# Deploy — 100% free tier

Stack (all free, no credit card needed except Render's optional verify):

| Piece     | Host    | Free?                          |
|-----------|---------|--------------------------------|
| Frontend  | Vercel  | Yes (Hobby)                    |
| Backend   | Render  | Yes (spins down when idle)     |
| Database  | Neon    | Yes (0.5 GB, no expiry)        |
| Cache     | none    | Yes (in-memory fallback)       |
| CI/tests  | GitHub Actions | Yes (public repo)       |
| Auth      | LINE / Google OAuth | Yes               |

There is nothing to pay to get this live. (Licensed market data is only needed
later, before you charge customers — see "Data" at the bottom.)

--------------------------------------------------------------------------------
## 0. Push to GitHub

```bash
cd quant-options-saas
git init && git add -A && git commit -m "initial"
git branch -M main
git remote add origin https://github.com/<you>/quant-options-saas.git
git push -u origin main
```
GitHub Actions runs the backend tests + frontend build automatically (see
`.github/workflows/ci.yml`). Check the "Actions" tab — green = everything passes.

--------------------------------------------------------------------------------
## 1. Database — Neon (free, permanent)

1. neon.tech -> sign up -> New Project.
2. Copy the connection string (starts `postgresql://...`). This is `DATABASE_URL`.

(You can skip Neon and let Render provision its own free Postgres via
`render.yaml`, but Render's free DB is deleted after ~30 days. Neon does not
expire, so it is the better free choice. If you use Neon, delete the
`databases:` block in `render.yaml` and set `DATABASE_URL` manually.)

--------------------------------------------------------------------------------
## 2. Backend — Render (free)

1. render.com -> New -> Blueprint -> connect the repo. It reads `render.yaml`.
2. Set the env vars marked `sync: false`:
   - `DATABASE_URL` = your Neon string (skip if using the bundled Render DB)
   - `CORS_ALLOWED_ORIGINS` = `https://<your-app>.vercel.app`
   - `CSRF_TRUSTED_ORIGINS` = `https://<your-app>.vercel.app`
   - `FRONTEND_URL` = `https://<your-app>.vercel.app`
   - `PROMPTPAY_ID`, `PROMPTPAY_NAME`
   - `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` (admin auto-created)
3. Deploy. The build runs migrate + seed_plans + ensure_superuser automatically.
4. Note the URL, e.g. `https://quant-options-api.onrender.com`.

Verify: open `https://<backend>/` -> `{"status":"ok",...}`. Admin at `/admin/`.

Note: free Render web services sleep after ~15 min idle; first request then takes
~30-60s to wake. Fine for an MVP.

--------------------------------------------------------------------------------
## 3. Frontend — Vercel (free)

1. vercel.com -> New Project -> import the repo.
2. Set **Root Directory = `frontend`**.
3. Env var: `NEXT_PUBLIC_API_URL = https://<backend>.onrender.com`
4. Deploy. Note the URL, e.g. `https://your-app.vercel.app`.
5. Go back to Render and make sure `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS`
   / `FRONTEND_URL` match this exact Vercel URL, then redeploy the backend.

--------------------------------------------------------------------------------
## 4. (Optional) LINE + Google login

1. Google Cloud Console -> OAuth client; LINE Developers -> Login channel.
2. Add redirect URIs:
   - `https://<backend>.onrender.com/accounts/google/login/callback/`
   - `https://<backend>.onrender.com/accounts/line/login/callback/`
3. Put `GOOGLE_CLIENT_ID/SECRET`, `LINE_CLIENT_ID/SECRET` in Render env, redeploy.
   (Filling any of them auto-enables allauth.)

--------------------------------------------------------------------------------
## 5. Test the live deployment (manual smoke test)

1. Open the Vercel URL -> Sign up with email -> you land on the dashboard.
2. GEX page (ES) loads levels (free tier).
3. Switch to NQ -> "needs a Pro plan" (gating works).
4. Account -> pick a plan -> upload any image as a slip -> submit.
5. Open `https://<backend>/admin/` -> Billing -> Payments -> select -> "Approve".
6. Back in the app, reload -> tier shows PRO -> NQ / Exposure / Chart / Vol now load.

--------------------------------------------------------------------------------
## Known free-tier limits

- **Uploaded slips are ephemeral** on Render free (filesystem resets on redeploy/
  sleep). Approve payments promptly, or wire free object storage (Cloudflare R2 /
  Supabase Storage) later. Approval data (tier, expiry) lives in Postgres and is
  safe.
- **Cold starts** on the free backend (~30-60s after idle).
- **Data licensing:** the app uses yfinance (Yahoo) + CBOE free feed — fine for
  testing, but NOT licensed for resale. Swap `backend/quant` data calls for a
  licensed vendor before charging customers.
