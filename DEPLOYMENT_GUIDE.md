# NEXORA MARKET — Deployment Guide (for the Backend Engineer)

Hi 👋 — this document is everything you need to deploy **NEXORA MARKET**, an
AI-powered market-intelligence web app. The frontend and backend are **already
integrated**: a single service serves both the website and the API on one URL.

**Estimated time to first deploy: ~10 minutes.**

---

## 1. What this is

- **Frontend:** `index.html` — a self-contained website (HTML + CSS + vanilla JS).
  No build step. Talks to the backend via `fetch`, and falls back to demo data if
  the API is unreachable.
- **Backend:** `backend/` — a **Python 3.11+ / FastAPI** app that aggregates five
  market-data providers, adds an AI explanation layer, and provides auth +
  watchlists.
- **Integration:** the FastAPI app **also serves the website** at `/`, so you only
  deploy **one service**. No CORS setup needed between them.

```
Browser ──HTTP──> FastAPI (backend/) ──> serves index.html at "/"
                                     └──> JSON API at "/api/*"
                                     └──> MarketAux / Finnhub / FMP /
                                          Alpha Vantage / Twelve Data + optional LLM
```

---

## 2. Repository layout

```
nexora-market/
├── index.html              # Frontend (served by the backend at "/")
├── assets/                 # Logo + favicon (served at "/assets")
├── backend/
│   ├── app/                # FastAPI application package
│   │   ├── main.py         # Entrypoint (also mounts the frontend)
│   │   ├── config.py       # Env-driven settings
│   │   ├── database.py     # Async SQLAlchemy models
│   │   ├── cache.py http.py schemas.py
│   │   ├── providers/      # marketaux, finnhub, fmp, alpha_vantage, twelve_data, mock
│   │   ├── services/       # market aggregation, ai engine, auth
│   │   └── routers/        # market, news, intelligence, auth, watchlist
│   ├── requirements.txt
│   ├── .env.example        # Copy to .env and fill in
│   ├── Dockerfile          # Backend-only image
│   ├── Procfile            # Heroku/Railway-style start command
│   └── run.sh              # Local dev runner
├── Dockerfile              # RECOMMENDED: single image (API + website)
├── docker-compose.yml
├── render.yaml             # 1-click Render.com blueprint
├── start.sh                # One-command local launcher
├── README.md               # Project overview
├── INTEGRATION.md          # How the frontend connects to the API
└── DEPLOYMENT_GUIDE.md     # (this file)
```

---

## 3. Configuration (environment variables)

Copy `backend/.env.example` to `backend/.env` and fill in what you have.
**The app runs with NO keys** (it serves clearly-labeled demo data) and unlocks
real data as keys are added.

| Variable | Required? | Purpose |
|---|---|---|
| `JWT_SECRET` | **Yes (prod)** | Long random string for signing auth tokens |
| `DATABASE_URL` | Recommended | Defaults to SQLite; use Postgres in prod (see §6) |
| `CORS_ORIGINS` | Optional | Comma-separated allowed origins (default `*`) |
| `ENV` | Optional | `production` in prod |
| `MARKETAUX_API_KEY` | Optional | News + sentiment |
| `FINNHUB_API_KEY` | Optional | Quotes, profiles, candles |
| `FMP_API_KEY` | Optional | Quotes, movers, sectors |
| `ALPHA_VANTAGE_API_KEY` | Optional | Quotes, daily series, news sentiment |
| `TWELVE_DATA_API_KEY` | Optional | Quotes + candles |
| `LLM_API_KEY` | Optional | OpenAI-compatible AI; without it a rule-based engine is used |
| `LLM_BASE_URL` / `LLM_MODEL` | Optional | LLM endpoint + model name |

> ⚠️ **Never commit `.env`.** It's already in `.gitignore`. Set secrets via your
> host's dashboard / secret manager.

Generate a JWT secret:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## 4. Deploy options (pick ONE)

### Option A — Docker (recommended, host-agnostic)
The **root** `Dockerfile` builds one image containing API + website.
```bash
docker build -t nexora-market .
docker run -p 8000:8000 --env-file backend/.env nexora-market
# open http://localhost:8000/
```
Or with compose:
```bash
docker compose up --build
```

### Option B — Render.com (free tier, fastest managed)
1. Push this repo to GitHub.
2. Render → **New + → Blueprint** → select the repo (it reads `render.yaml`).
3. Add the provider API keys in the dashboard.
4. Deploy → you get a public `https://...onrender.com` URL.

### Option C — Railway / Fly.io / Heroku
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Root directory: `backend/` (the `Procfile` already contains this).
- For Fly.io, the root `Dockerfile` works with `fly launch`.

### Option D — Bare VM (Ubuntu + systemd + Nginx)
```bash
sudo apt update && sudo apt install -y python3-venv
cd /opt && git clone <your-repo> nexora && cd nexora/backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt gunicorn
cp .env.example .env   # edit it
# run with gunicorn + uvicorn workers:
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 -w 2
```
Then put Nginx in front (TLS, reverse proxy to `:8000`). See §7 for the unit/proxy
snippets.

---

## 5. Verify the deployment (smoke test)

After it's running, hit these (replace host):
```bash
BASE=http://localhost:8000

curl -s $BASE/health                       # {"status":"ok", "providers":{...}}
curl -s $BASE/ | grep -o "<title>.*</title>"   # the website
curl -s $BASE/api/market/movers/gainers    # market data
curl -s $BASE/api/ai/analyze/AAPL          # AI analysis
curl -s -X POST $BASE/api/ai/chat -H "Content-Type: application/json" \
     -d '{"message":"Why is GTCO rising?"}'

# auth + watchlist
TOKEN=$(curl -s -X POST $BASE/api/auth/signup -H "Content-Type: application/json" \
  -d '{"name":"QA","email":"qa@example.com","password":"secret123"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -X POST $BASE/api/watchlist -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"symbol":"AAPL"}'
```
Interactive API docs are auto-generated at **`/docs`** (Swagger) and **`/redoc`**.

---

## 6. Production checklist

- [ ] Set a strong `JWT_SECRET`.
- [ ] Set `ENV=production`.
- [ ] Restrict `CORS_ORIGINS` to your real domain(s) instead of `*`.
- [ ] **Use Postgres** instead of SQLite for multi-instance / persistence:
      `DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/nexora`
      then `pip install asyncpg`. (Tables auto-create on startup.)
- [ ] Serve behind HTTPS (managed hosts do this automatically).
- [ ] Add provider API keys (otherwise data is demo/mock — clearly labeled).
- [ ] (Optional) Add `LLM_API_KEY` to upgrade AI explanations from rule-based to LLM.
- [ ] (Optional) Swap the in-memory cache (`app/cache.py`) for Redis if you scale
      horizontally — same `get/set` interface.

---

## 7. Nginx + systemd (Option D reference)

`/etc/systemd/system/nexora.service`
```ini
[Unit]
Description=Nexora Market
After=network.target

[Service]
WorkingDirectory=/opt/nexora/backend
EnvironmentFile=/opt/nexora/backend/.env
ExecStart=/opt/nexora/backend/.venv/bin/gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 -w 2
Restart=always

[Install]
WantedBy=multi-user.target
```
Nginx server block:
```nginx
server {
    server_name nexora.example.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Then `sudo certbot --nginx` for TLS.

---

## 8. API reference (quick)

Base: `/api`

| Group | Endpoints |
|---|---|
| Market | `GET /market/quote/{symbol}`, `/market/quotes?symbols=`, `/market/candles/{symbol}`, `/market/movers/{gainers\|losers\|trending\|active}`, `/market/sectors`, `/market/sentiment`, `/market/overview` |
| News | `GET /news?symbols=&market=&category=&limit=` |
| AI | `GET /ai/analyze/{symbol}`, `GET /ai/insights`, `POST /ai/chat` |
| Auth | `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`, `POST /auth/upgrade` |
| Watchlist | `GET /watchlist`, `GET /watchlist/quotes`, `POST /watchlist`, `DELETE /watchlist/{symbol}` |

Full schema is live at `/docs` once deployed. More detail in `backend/README.md`.

---

## 9. Notes / gotchas

- **Frontend ↔ backend wiring:** `index.html` auto-detects the API at the same
  origin it's served from. Since the backend serves the page, this just works.
  To point the frontend at a *different* API host, set
  `window.NEXORA_API_BASE` in the `<head>` of `index.html`, or append
  `?api=https://api.example.com` to the URL. (See `INTEGRATION.md`.)
- **Database migrations:** none needed for first deploy — tables auto-create on
  startup. If you later change models, add Alembic.
- **Disclaimer:** the product shows market intelligence / educational info only —
  not financial advice. Keep the footer disclaimer intact.

Questions about anything here? The code is well-commented; start at
`backend/app/main.py`.
