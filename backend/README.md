# NEXORA MARKET — Backend API

AI-powered market-intelligence backend that aggregates **five** market-data
providers behind one clean, well-documented API. Built with **FastAPI** (async),
with JWT auth, watchlists, in-memory caching, graceful provider fallback, and a
**pluggable AI layer** (LLM when a key is present, deterministic rule-based
plain-language engine otherwise).

> **Educational market intelligence only — not financial advice.**

---

## ✨ Features

- **5 data providers, 1 API** with automatic priority + fallback:
  | Capability | Priority chain |
  |-----------|----------------|
  | Quotes    | Finnhub → Twelve Data → FMP → Alpha Vantage → mock |
  | Candles   | Twelve Data → Alpha Vantage → Finnhub → mock |
  | Movers    | FMP → mock |
  | Sectors   | FMP → mock |
  | News      | MarketAux → Alpha Vantage → Finnhub → mock |
- **Works with zero keys** — returns clearly-labeled `source: "mock"` data so the
  frontend is never blocked. Add keys to progressively unlock real data.
- **Plain-language AI** — every explanation is beginner-friendly (no jargon).
  Uses an OpenAI-compatible LLM when `LLM_API_KEY` is set, otherwise a built-in
  rule-based engine.
- **Auth + watchlists** — JWT signup/login, free plan (5 stocks) vs premium
  (unlimited) enforced server-side.
- **Caching + resilience** — TTL cache, retries with backoff, 429 handling,
  per-provider isolation (one failing provider never breaks a request).
- **Self-documenting** — interactive Swagger UI at `/docs`, ReDoc at `/redoc`.

---

## 🚀 Quick start

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optional: add your API keys
./run.sh                      # or: uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs**.

### Docker
```bash
docker build -t nexora-api .
docker run -p 8000:8000 --env-file .env nexora-api
```

---

## 🔑 Configuration

All config is via environment variables (see `.env.example`). Keys are optional.

| Var | Purpose |
|-----|---------|
| `MARKETAUX_API_KEY` | News + entity sentiment |
| `FINNHUB_API_KEY` | Quotes, profiles, candles, company news |
| `FMP_API_KEY` | Quotes, market movers, sector performance |
| `ALPHA_VANTAGE_API_KEY` | Quotes, daily series, news sentiment |
| `TWELVE_DATA_API_KEY` | Quotes + time-series candles |
| `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` | Optional OpenAI-compatible AI |
| `JWT_SECRET` | Token signing secret (set in production!) |
| `DATABASE_URL` | Defaults to local SQLite |
| `CACHE_TTL_SECONDS` | Quote cache lifetime (default 60) |
| `CORS_ORIGINS` | Comma-separated allowed origins |

---

## 📚 API reference

Base URL: `http://localhost:8000`

### Meta
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info + disclaimer |
| GET | `/health` | Status, active providers, AI mode |

### Market  `/api/market`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/quote/{symbol}` | Single live quote |
| GET | `/quotes?symbols=AAPL,TSLA` | Batch quotes |
| GET | `/candles/{symbol}?count=60` | OHLC candles |
| GET | `/movers/{category}` | `gainers\|losers\|trending\|active` (+AI summaries) |
| GET | `/sectors` | Sector performance |
| GET | `/sentiment` | Overall market sentiment score |
| GET | `/overview` | Everything for the homepage in one call |

### News  `/api/news`
| GET | `/api/news?symbols=&market=&category=&limit=` | Filtered news w/ AI summaries |

`market` = `nigeria\|us\|global`; `category` = `banking\|tech\|energy\|consumer\|all`

### AI Intelligence  `/api/ai`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/analyze/{symbol}` | Full plain-language analysis (trend, sentiment, risk, news, explanation) |
| GET | `/insights` | Dynamic AI insight cards |
| POST | `/chat` | Conversational assistant (`{message, history}`) |

### Auth  `/api/auth`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/signup` | Create account → returns JWT |
| POST | `/login` | Login → returns JWT |
| GET | `/me` | Current user (Bearer token) |
| POST | `/upgrade` | Switch to premium (demo) |

### Watchlist  `/api/watchlist`  *(auth required)*
| Method | Path | Description |
|--------|------|-------------|
| GET | `` | List items |
| GET | `/quotes` | List items + live quotes |
| POST | `` | Add `{symbol, name?}` (free limit = 5) |
| DELETE | `/{symbol}` | Remove |

---

## 🧪 Example requests

```bash
# Market overview (homepage)
curl http://localhost:8000/api/market/overview

# AI analysis of a stock
curl http://localhost:8000/api/ai/analyze/TSLA

# Ask the assistant
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Why is GTCO rising?"}'

# Sign up, then add to watchlist
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane","email":"jane@example.com","password":"secret123"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -X POST http://localhost:8000/api/watchlist \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL"}'
```

---

## 🗂 Project structure

```
backend/
├── app/
│   ├── main.py            # FastAPI app + router wiring
│   ├── config.py          # env-driven settings
│   ├── cache.py           # async TTL cache
│   ├── http.py            # shared async client + retries
│   ├── schemas.py         # pydantic models
│   ├── database.py        # async SQLAlchemy models
│   ├── providers/         # one module per data provider (+ mock)
│   │   ├── marketaux.py  finnhub.py  fmp.py
│   │   ├── alpha_vantage.py  twelve_data.py  mock.py
│   ├── services/
│   │   ├── market.py      # aggregation + fallback orchestration
│   │   ├── ai.py          # LLM + rule-based explanation engine
│   │   └── auth.py        # hashing + JWT
│   └── routers/           # market, news, intelligence, auth, watchlist
├── requirements.txt
├── Dockerfile
├── run.sh
└── .env.example
```

---

## 🔌 Connecting the frontend

Point the website at this API and replace the demo JS data with `fetch` calls,
e.g. the homepage market section → `GET /api/market/overview`, the analyzer →
`GET /api/ai/analyze/{symbol}`, the assistant → `POST /api/ai/chat`. CORS is
open by default in development.
