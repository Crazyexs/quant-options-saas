# Quant Options SaaS

Paid, role-gated web platform built from the Streamlit app's quant engine.
Backend: Django REST. Frontend: Next.js. Auth: email + JWT (LINE/Google via
allauth). Payments: manual PromptPay + Django Admin approval.

- Full design: `ARCHITECTURE.md`
- **Deploy for free (Vercel + Render + Neon): `DEPLOY.md`**
- This README: how to run it locally.

```
quant-options-saas/
  ARCHITECTURE.md
  backend/    Django + DRF (reuses quant/gex_core.py etc.)
  frontend/   Next.js + Tailwind
```

--------------------------------------------------------------------------------
## Run the backend (local)

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements.txt
copy .env.example .env                              # then edit .env
python manage.py makemigrations accounts billing
python manage.py migrate
python manage.py seed_plans
python manage.py createsuperuser
python manage.py runserver
```

With no `DATABASE_URL` / `REDIS_URL` it uses SQLite + in-memory cache, so it runs
with zero external services. API is at http://localhost:8000, admin at /admin/.

Key endpoints:
- `POST /api/auth/register/`  `POST /api/auth/token/`  `GET /api/auth/me/`
- `GET  /api/gex/?symbol=ES`  (free: ES; pro: any)  `GET /api/gex/all/` (pro)
- `GET  /api/exposure/?symbol=ES&greek=GEX` (pro)  `GET /api/chain/?symbol=ES` (pro)
- `GET  /api/vol/surface/?symbol=ES` (elite)
- `GET  /api/macro/nq-bias/` (pro)  `GET /api/macro/events/` (free)
- `GET  /api/fundamentals/?symbol=NVDA` (pro)
- `GET  /api/billing/plans/`  `GET /api/billing/promptpay/`  `POST /api/billing/promptpay/submit/`

--------------------------------------------------------------------------------
## Run the frontend (local)

```bash
cd frontend
npm install
copy .env.example .env.local        # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:3000 -> sign up -> dashboard.

--------------------------------------------------------------------------------
## Manual PromptPay payment flow

1. Set `PROMPTPAY_ID` / `PROMPTPAY_NAME` in backend `.env`.
2. User goes to Account, selects a plan, uploads their bank slip.
3. A `Payment(pending)` is created with the slip image.
4. You open `/admin/` -> Billing -> Payments -> select -> "Approve selected
   payments". Approval sets the user's tier + extends `subscription_until`.
5. The user's access unlocks immediately on their next request.

Plans are seeded by `python manage.py seed_plans` (edit in
`billing/management/commands/seed_plans.py` or in the admin).

--------------------------------------------------------------------------------
## Enable Discord login (end-to-end, already wired)

The flow: frontend link -> `/accounts/discord/login/` -> Discord OAuth ->
allauth logs the user in -> `social_complete` mints a JWT -> redirects to
`FRONTEND_URL/auth/callback?access=...&refresh=...` -> the SPA stores the tokens.
Credentials come from settings (no DB SocialApp needed).

1. discord.com/developers -> New Application -> OAuth2.
2. Add redirect URI: `https://<backend>/accounts/discord/login/callback/`
   (locally: `http://localhost:8000/accounts/discord/login/callback/`).
3. Put `DISCORD_CLIENT_ID` / `DISCORD_CLIENT_SECRET` in backend `.env` and set
   `FRONTEND_URL`. Setting these auto-enables allauth.
4. The login page's "Continue with Discord" button links to
   `/accounts/discord/login/`; the `/auth/callback` page completes sign-in.

Note: Discord returns an email when the user grants the email scope and has a
verified email; otherwise `SocialAdapter` synthesizes a placeholder email from
the Discord uid.

--------------------------------------------------------------------------------
## Deploy (free)

See **`DEPLOY.md`** for the full free-tier walkthrough: Vercel (frontend) +
Render (backend, via `render.yaml`) + Neon (free Postgres). Migrations, plan
seeding, and the admin user are all created automatically at deploy time by
`backend/build.sh` — no shell steps required. A `Dockerfile` + `railway.json`
are also included if you prefer Railway/Docker.

--------------------------------------------------------------------------------
## What is scaffolded vs TODO

Done: project structure, custom User + tiers, JWT auth, tier-gating permission,
all market endpoints wrapping the quant core with Redis caching, billing models +
PromptPay slip upload + admin approval + plan seeding, frontend landing / login /
dashboard (GEX, exposure, chain, macro, fundamentals, account/pay).

TODO before charging money:
- **Data licensing.** yfinance (Yahoo) + CBOE free feed are NOT licensed for
  resale. Swap `backend/quant` data calls for a licensed vendor (Polygon /
  Databento / Tradier / CBOE paid). The data layer is the only thing to change.
- Move JWT from localStorage to httpOnly cookies for production security.
- Charts (TradingView Lightweight Charts / Plotly) on the analytics pages.
- Celery beat job to expire lapsed subscriptions (currently checked lazily on
  each request via `User.effective_tier`).
- Thai PDPA: consent, privacy policy, slip-image retention/deletion.
- Disclaimers everywhere ("not investment advice", delayed data).

NOTE: This was scaffolded without a local Python/Node runtime, so it is
inspection-verified, not run-tested. Expect to run migrations and fix any small
version/import issues on first boot.
