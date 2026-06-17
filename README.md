# NEXORA MARKET — AI Market Intelligence (Full Stack)

> **Understand the Market. Stay Ahead.**
> A premium, AI-powered market-intelligence platform. Frontend + backend are
> **fully integrated and deploy-ready** — one service serves the website *and*
> the API on a single URL.

![tagline](https://img.shields.io/badge/AI-Market%20Intelligence-2563EB) ![stack](https://img.shields.io/badge/FastAPI-Python%203.12-06B6D4) ![status](https://img.shields.io/badge/status-deploy%20ready-10B981)

---

## ⚡ TL;DR — run it in one command

```bash
./start.sh
```

Then open **http://localhost:8000/** — the full website, backed by the live API.
(First run auto-creates a venv, installs deps, and copies a default `.env`.)

> Works out-of-the-box with clearly-labeled **demo data**. Add real provider keys
> in `backend/.env` to switch to live market data.

---

## 🧩 What's inside

```
nexora-market/
├── index.html              # Complete frontend (HTML + CSS + JS, self-contained)
├── assets/                 # Brand logo + favicon
├── backend/                # FastAPI backend (aggregates 5 market-data APIs)
│   ├── app/
│   │   ├── main.py         # App + serves the website at "/"
│   │   ├── config.py  cache.py  http.py  schemas.py  database.py
│   │   ├── providers/      # marketaux, finnhub, fmp, alpha_vantage, twelve_data, mock
│   │   ├── services/       # market aggregation, AI engine, auth
│   │   └── routers/        # market, news, intelligence, auth, watchlist
│   ├── requirements.txt  Dockerfile  Procfile  run.sh  .env.example
├── Dockerfile              # Single image: API + website
├── docker-compose.yml
├── render.yaml             # 1-click Render.com blueprint
├── start.sh                # One-command local launcher
├── INTEGRATION.md          # How the frontend talks to the backend
└── README.md
```

---

## ✨ Features

**Frontend** (premium dark fintech UI, fully responsive)
- Hero, live ticker, market overview, AI insights, stock analyzer, news center,
  AI assistant chat, watchlist, pricing, mobile-app preview, testimonials, auth,
  newsletter, footer — all wired to the backend with graceful demo fallback.

**Backend** (FastAPI, async)
- **5 providers, 1 API** with automatic priority + fallback:
  MarketAux · Finnhub · FMP · Alpha Vantage · Twelve Data.
- **Plain-language AI** explanations (rule-based engine, optional LLM upgrade).
- JWT **auth** + **watchlists** (free = 5 stocks, premium = unlimited).
- Caching, retries, rate-limit handling, CORS, Swagger docs at `/docs`.
- **Works with zero keys** (labeled mock data) → progressively unlocks real data.

---

## 🚀 Deploy options

### 1) Render.com (easiest — free tier)
1. Push this repo to GitHub.
2. On Render: **New + → Blueprint**, pick the repo (it reads `render.yaml`).
3. Add your provider API keys in the dashboard. Done — you get a public URL.

### 2) Docker (anywhere)
```bash
docker build -t nexora-market .
docker run -p 8000:8000 --env-file backend/.env nexora-market
# → http://localhost:8000/
```
or:
```bash
docker compose up --build
```

### 3) Railway / Fly.io / any host
Use the `backend/Procfile` (`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
with project root `backend/`. The Dockerfile also works on Fly.io
(`fly launch`).

### 4) Local (no Docker)
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add keys (optional)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Public link in 30 seconds (local + tunnel)
```bash
./start.sh                          # terminal 1
npx ngrok http 8000                 # terminal 2  → public https URL
# or: cloudflared tunnel --url http://localhost:8000
```

---

## 🔑 Configuration (`backend/.env`)

| Variable | Purpose |
|---|---|
| `MARKETAUX_API_KEY` | News + sentiment |
| `FINNHUB_API_KEY` | Quotes, profiles, candles |
| `FMP_API_KEY` | Quotes, movers, sectors |
| `ALPHA_VANTAGE_API_KEY` | Quotes, daily series, news sentiment |
| `TWELVE_DATA_API_KEY` | Quotes + candles |
| `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` | Optional OpenAI-compatible AI |
| `JWT_SECRET` | **Set a long random value in production** |
| `DATABASE_URL` | Defaults to SQLite; use Postgres in prod |
| `CORS_ORIGINS` | Comma-separated allowed origins |

All keys are optional — the app runs in demo mode without them.

---

## 📚 Key URLs (once running)

| URL | What |
|---|---|
| `/` | The website |
| `/docs` | Interactive API docs (Swagger) |
| `/redoc` | API docs (ReDoc) |
| `/health` | Status + active providers + AI mode |
| `/api/...` | All API endpoints (see `backend/README.md`) |

---

## ⚖️ Disclaimer

Nexora Market provides market intelligence and educational information only.
It does **not** provide financial or investment advice.
