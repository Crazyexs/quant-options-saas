# Quant Options SaaS — Architecture Specification

Version 0.1 (planning). No code yet — this document is the build plan, agreed
before scaffolding. It reuses the Python quant logic from the existing Streamlit
app (`gex_core.py`, `chain_core.py`, `macro_core.py`) and turns it into a paid,
role-gated web product for a primarily Thai audience.

--------------------------------------------------------------------------------
## 1. Goals

- Sell access to the GEX / options-exposure analytics (entry cost / subscription).
- Login with LINE (primary, Thailand) and Google (fallback).
- Gate features by paid tier (free / pro / elite).
- Take payment via PromptPay QR, approved manually through an admin panel (MVP).
- Professional trading-platform UI, not a "bot" or terminal look.
- Reuse the existing Python quant math verbatim — no rewrite of the formulas.

--------------------------------------------------------------------------------
## 2. Final tech stack (per decisions)

| Layer        | Choice                              | Host    |
|--------------|-------------------------------------|---------|
| Frontend     | Next.js (App Router) + TypeScript   | Vercel  |
| UI / design  | Tailwind CSS + shadcn/ui            | Vercel  |
| Charts       | TradingView Lightweight Charts (price) + Plotly.js (3D/heatmap) | Vercel |
| Backend      | Django + Django REST Framework      | Railway |
| Quant core   | Copied gex_core / chain_core / macro_core (Python) | Railway |
| Auth         | django-allauth (LINE + Google) + SimpleJWT | Railway |
| Database     | PostgreSQL                          | Railway |
| Cache        | Redis (shared market-data cache)    | Railway |
| Payments     | Manual PromptPay QR + Django Admin approval | Railway |
| Background   | Celery + Redis (subscription expiry, cache warm) | Railway |

--------------------------------------------------------------------------------
## 3. High-level architecture

```
        Browser
          |
          v
  Next.js (Vercel)  --- httpOnly JWT cookie --->  Django REST (Railway)
   - marketing/pricing                              |   accounts (LINE/Google, JWT, tiers)
   - /app dashboard (gated)                         |   billing (PromptPay slips, admin approve)
   - charts                                         |   market  (wraps quant core)
                                                     |
                          +--------------------------+--------------------------+
                          |                          |                          |
                     PostgreSQL                   Redis cache               Data layer
                  (users, subs,                (CBOE/yf pulls,            (yfinance/CBOE now;
                   payments)                    shared, 60-120s TTL)       licensed feed later)
```

Key idea: the **market-data fetch happens once per symbol per cache window** on
the server and is shared across all users. Individual users never hit CBOE/Yahoo
directly (avoids IP bans and rate limits).

--------------------------------------------------------------------------------
## 4. Repository layout (monorepo)

```
quant-options-saas/
  ARCHITECTURE.md                 <- this file
  backend/                        Django + DRF
    config/                       settings (split: base/dev/prod), urls, wsgi, celery
    accounts/                     custom User, social auth, JWT, Tier enum
    billing/                      Plan, Subscription, Payment(slip), admin approval
    market/
      quant/                      COPIED: gex_core.py, chain_core.py, macro_core.py
      services.py                 data-layer abstraction + Redis caching
      serializers.py views.py urls.py
    common/                       permissions (tier gating), throttling, pagination
    manage.py requirements.txt Dockerfile railway.json
  frontend/                       Next.js
    app/
      (marketing)/                landing, pricing, about
      (auth)/login                LINE/Google buttons
      app/                        gated dashboard
        gex/ exposure/ vol/ chain/ oi/ macro/ chart/
      account/ pay/               subscription + PromptPay slip upload
    components/  lib/  styles/
    package.json next.config.js
```

Two deploy targets, one repo: Vercel builds `frontend/`, Railway builds `backend/`.

--------------------------------------------------------------------------------
## 5. Backend design (Django REST)

### 5.1 Django apps
- **accounts** — custom `User`, social login, JWT, `tier` field.
- **billing** — `Plan`, `Subscription`, `Payment` (PromptPay slip), admin approval.
- **market** — read-only API wrapping the quant core; tier-gated.
- **common** — reusable permissions, throttles, caching helpers.

### 5.2 Data-layer abstraction (important for the data swap)
`market/services.py` exposes one interface so the licensed-feed migration is a
single-file change:
```
class MarketDataSource(Protocol):
    def cboe_chain(symbol) -> dict
    def spot(symbol) -> float

class FreeSource(MarketDataSource):   # yfinance + CBOE CDN (today)
class VendorSource(MarketDataSource): # Polygon/Databento/Tradier (later)
```
The quant core (`gex_core` etc.) is called by services, results cached in Redis.

### 5.3 API endpoints (all read-only, JSON)
```
Auth / account
  POST /api/auth/line/        social login -> issues JWT
  POST /api/auth/google/
  POST /api/auth/refresh/
  GET  /api/auth/me/          { email, tier, subscription_until }

Market (tier-gated)
  GET  /api/gex/?symbol=ES            -> gex_core.compute_symbol      [free: ES only]
  GET  /api/gex/all/                  -> gex_core.compute_all         [pro+]
  GET  /api/exposure/?symbol=&greek=  -> chain_core.aggregate_greek   [pro+]
  GET  /api/chain/?symbol=&expiry=    -> chain_core.load_chain        [pro+]
  GET  /api/vol/surface/?symbol=      -> chain_core IV surface        [elite]
  GET  /api/oi/?symbol=               -> chain_core OI                [pro+]
  GET  /api/macro/nq-bias/            -> macro_core.compute_nq_bias   [pro+]
  GET  /api/macro/events/            -> macro_core.event_risk        [free]

Billing
  GET  /api/billing/plans/
  GET  /api/billing/subscription/
  POST /api/billing/promptpay/submit/   multipart: plan + slip image
```

### 5.4 Tier gating
Custom DRF permission:
```
class HasTier(BasePermission):
    def __init__(self, min_tier): ...
    # compares request.user.tier against min_tier; checks subscription not expired
```
Each view declares `permission_classes = [IsAuthenticated, HasTier("pro")]`.
Enforced server-side — the frontend also hides locked features, but the API is
the source of truth.

--------------------------------------------------------------------------------
## 6. Authentication flow (LINE + Google)

- Use **django-allauth** providers `line` and `google` for the OAuth dance.
- On success, issue a **SimpleJWT** access token (short, ~15 min) + refresh token
  (~14 days) set as **httpOnly, Secure, SameSite=None** cookies (cross-site: Vercel
  domain -> Railway domain), with CORS locked to the Vercel origin.
- `GET /api/auth/me/` returns the user + tier so the frontend can render state.

```
User clicks "Login with LINE" (Next.js)
   -> redirect to LINE OAuth
   -> callback to Django allauth
   -> Django creates/links User, issues JWT cookies
   -> redirect back to /app ; frontend calls /api/auth/me
```

LINE provider needs a LINE Login channel (LINE Developers Console). Google needs
an OAuth client (Google Cloud Console). Both free.

--------------------------------------------------------------------------------
## 7. Manual PromptPay payment flow (MVP)

No payment-gateway integration or fees. Admin approves slips in Django Admin.

```
1. User picks a plan on /pay
2. Frontend shows your PromptPay QR (static QR, or generated with the amount)
3. User pays in their bank app, screenshots the slip
4. User uploads slip -> POST /api/billing/promptpay/submit
5. Payment row created: status=PENDING, with slip image + plan + user
6. You open Django Admin -> Payments -> verify the slip -> click "Approve"
7. Approval action sets Subscription.active, tier=plan.tier,
   expires_at = now + plan.duration; user instantly unlocked
```

Models:
```
Plan         (code, name, price_thb, tier, duration_days)
Payment      (user, plan, slip_image, amount, status, created_at, reviewed_by)
Subscription (user, tier, started_at, expires_at, is_active)
```

Admin custom action `approve_payments` does the upgrade atomically. A Celery
beat job downgrades expired subscriptions daily.

Upgrade path later: auto-verify slips via a Thai slip-verification API
(e.g. SlipOK) to remove the manual step; or move to Stripe/Omise PromptPay.

--------------------------------------------------------------------------------
## 8. Tier / feature matrix

| Feature                         | Free | Pro | Elite |
|---------------------------------|------|-----|-------|
| GEX day-trade levels (ES only)  | yes  | yes | yes   |
| All symbols (ES/NQ/GC)          | no   | yes | yes   |
| DEX / VEX / Vega / Charm        | no   | yes | yes   |
| Option chain + Greeks           | no   | yes | yes   |
| Open interest / volume          | no   | yes | yes   |
| NQ macro bias                   | no   | yes | yes   |
| Macro event calendar            | yes  | yes | yes   |
| IV 3D surface / vol heatmap     | no   | no  | yes   |
| Snapshot logging + backtest     | no   | no  | yes   |
| Alerts (wall touch / flip cross)| no   | no  | yes   |
| API access                      | no   | no  | yes   |

Prices (suggested, THB/month): Free 0, Pro 590, Elite 1,490 — tune later.

--------------------------------------------------------------------------------
## 9. Frontend design (professional, not bot-like)

- **App Router + TypeScript + Tailwind + shadcn/ui** component system.
- Design tokens (dark, modern fintech — Linear/Vercel meets trading terminal):
  - background `#0B0E11`, surface `#151A21`, border `#222A33`
  - text `#E6EAF0`, muted `#8A94A6`
  - up/positive `#16C784`, down/negative `#EA3943`, accent `#3B82F6`
  - font: Inter (UI), IBM Plex Mono (numbers/tables)
- **TradingView Lightweight Charts** for price candles + level overlays (looks
  instantly professional). **Plotly.js** only for the 3D IV/exposure surfaces.
- Layout: left nav rail (function list), top bar (symbol switcher, account/tier
  badge), main grid of cards. Locked features show a subtle "Upgrade" overlay.
- `lib/api.ts` typed client; auth via the httpOnly cookie (credentials: include).

Frontend routes mirror the endpoints: `/app/gex`, `/app/exposure`, `/app/vol`,
`/app/chain`, `/app/oi`, `/app/macro`, `/app/chart`, plus `/pricing`, `/pay`,
`/account`.

--------------------------------------------------------------------------------
## 10. Streamlit page -> new app mapping

| Streamlit page (old)        | API endpoint                | Frontend route   | Tier  |
|-----------------------------|-----------------------------|------------------|-------|
| GEX Day-Trade               | /api/gex, /api/gex/all      | /app/gex         | free* |
| NQ Macro Bias               | /api/macro/nq-bias          | /app/macro       | pro   |
| DEX / VEX / Vega / Charm    | /api/exposure?greek=        | /app/exposure    | pro   |
| Option Chain                | /api/chain                  | /app/chain       | pro   |
| Vol Heatmap (+3D)           | /api/vol/surface            | /app/vol         | elite |
| Exposure Ladder             | /api/exposure (composed)    | /app/gex (ladder)| pro   |
| Open Interest               | /api/oi                     | /app/oi          | pro   |
| Contract Chart              | /api/gex + price feed        | /app/chart       | pro   |
| Macro News                  | /api/macro/events           | /app/macro       | free  |

*Free = ES only.

--------------------------------------------------------------------------------
## 11. Deployment

- **Railway project** with services: Django web (gunicorn/uvicorn), Postgres,
  Redis, Celery worker + beat. Env: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`,
  `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, LINE/Google client IDs+secrets,
  `PROMPTPAY_ID`. Dockerfile + `railway.json`.
- **Vercel project** for `frontend/`. Env: `NEXT_PUBLIC_API_URL` (Railway URL).
- Custom domains: `app.yourdomain.com` (Vercel) + `api.yourdomain.com` (Railway).
- CORS: backend allows only the Vercel origin; cookies `SameSite=None; Secure`.

--------------------------------------------------------------------------------
## 12. Caching & rate-limit strategy

- Redis key per `(symbol, function)`; TTL 60-120s (matches CBOE delay).
- A Celery beat task warms the cache for ES/NQ/GC every 60s so user requests are
  always cache hits.
- DRF throttling per user/tier to stop abuse of the elite API access.

--------------------------------------------------------------------------------
## 13. Legal / compliance (must address before charging)

- **Data licensing:** yfinance (Yahoo) and the CBOE free CDN are NOT licensed for
  commercial resale. Before taking money, migrate the data layer (section 5.2) to
  a licensed vendor (Polygon, Databento, Tradier, or CBOE paid). Architecture is
  unchanged; only `VendorSource` is added.
- **Thai PDPA:** you store user identity + payment slips. Add a consent checkbox,
  a privacy policy, slip-image retention limits, and deletion on request.
- **Disclaimers:** "not investment advice", delayed-data notice, no profit
  guarantee — on the marketing site and inside the app.

--------------------------------------------------------------------------------
## 14. Phased roadmap

- **Phase 0 — Backend parity (no auth).** Scaffold Django, copy quant core, expose
  public endpoints, confirm numbers match the Streamlit app. Add Redis cache.
- **Phase 1 — Auth + tiers.** allauth LINE+Google, JWT cookies, `HasTier` gating.
- **Phase 2 — Billing.** Plans, PromptPay slip upload, Django Admin approval,
  subscription model + expiry job.
- **Phase 3 — Frontend.** Next.js pro UI, charts, gated dashboard, pricing/pay.
- **Phase 4 — Hardening.** Licensed data swap, alerts, throttling, PDPA, polish.

--------------------------------------------------------------------------------
## 15. Rough monthly cost (MVP)

- Railway: ~$5-20 (web + Postgres + Redis + worker, hobby tier).
- Vercel: free (Hobby) or $20 (Pro).
- Domain: ~$10-15/year.
- LINE Login, Google OAuth, PromptPay (manual): free.
- Licensed data (Phase 4): from ~$30-200+/mo depending on vendor — the main
  variable cost once you charge customers.

--------------------------------------------------------------------------------
## 16. Open decisions to confirm before Phase 0

1. Plan prices and exact tier feature split (section 8 is a draft).
2. Subscription length: monthly only, or also weekly / lifetime?
3. One PromptPay account/QR for everything, or per-amount generated QR?
4. Domain name.
5. Data vendor target for Phase 4 (affects cost + which fields are available).
