# NEXORA MARKET — Frontend ↔ Backend Integration

The website (`index.html`) is now **live-first**: it calls the NEXORA backend API
for real data, and **gracefully falls back to built-in demo data** whenever the
backend isn't reachable (e.g. the no-network preview, or `file://`). You never
see a broken page.

---

## How it works

A small API client (`NEXORA`) is embedded in `index.html`:

- **Auto-detects** the backend base URL:
  1. `?api=` query param  → e.g. `index.html?api=http://localhost:8000`
  2. `window.NEXORA_API_BASE` (set in the `<head>` config block)
  3. `localStorage.nexora_api_base`
  4. Same host on **port 8000** when served over http/https
  5. Otherwise (preview / `file://`) → **no backend → demo data**
- Every request has a **short timeout** and a **try/catch fallback**, so a slow
  or missing API instantly drops back to demo content.
- The JWT token is persisted in `localStorage` so sessions survive refresh.

---

## What's wired to the API

| Section | Endpoint(s) |
|---|---|
| Live ticker | `GET /api/market/quotes?symbols=…` |
| Market Overview (Gainers/Losers/Trending/Active) | `GET /api/market/movers/{category}` |
| Market Sentiment gauge | `GET /api/market/sentiment` |
| Sector Performance | `GET /api/market/sectors` |
| AI Insight cards | `GET /api/ai/insights` |
| Stock Analyzer (search) | `GET /api/ai/analyze/{symbol}` (+ live candle chart) |
| News Center (filters) | `GET /api/news?market=&category=&limit=` |
| AI Assistant chat | `POST /api/ai/chat` (with conversation history) |
| Sign Up / Login | `POST /api/auth/signup` · `POST /api/auth/login` |
| Session restore | `GET /api/auth/me` |
| Upgrade to Premium | `POST /api/auth/upgrade` |
| Watchlist (view/add/remove) | `GET /api/watchlist/quotes` · `POST /api/watchlist` · `DELETE /api/watchlist/{symbol}` |

When the watchlist loads for a signed-in user, an **"Add symbol"** input appears
in the panel and each row gets a remove (×) button. Free-plan users are limited
to 5 stocks (enforced by the backend); the error is shown inline. After
**Upgrade to Premium**, the limit is lifted.

A **"Live data · powered by …"** chip appears under the Markets heading when real
provider data is being served (hidden in mock mode).

---

## Run it locally (full stack)

**1. Start the backend** (port 8000):
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # add provider/LLM keys (optional)
./run.sh                    # http://localhost:8000/docs
```

**2. Serve the frontend** (any static server; same host so port-8000
auto-detection works):
```bash
cd ..
python3 -m http.server 3000
# open http://localhost:3000/index.html
```

That's it — the page auto-connects to `http://localhost:8000`.

### Point at a different backend
- URL param: `http://localhost:3000/index.html?api=https://api.nexora.market`
- Or edit the config block in `index.html` `<head>`:
  ```html
  <script>window.NEXORA_API_BASE = "https://api.nexora.market";</script>
  ```
- Or in the browser console:
  ```js
  localStorage.setItem('nexora_api_base','https://api.nexora.market'); location.reload();
  ```

---

## Notes

- **Preview / offline:** with no backend, every section renders the original
  polished demo data — nothing breaks.
- **CORS:** open by default in development (`CORS_ORIGINS` in `.env`).
- **Real market data:** add provider keys to `backend/.env` to replace the
  labeled mock data with live quotes/news. See `backend/README.md`.
- **Real AI:** add `LLM_API_KEY` to upgrade the assistant/analyzer explanations
  from the rule-based engine to an LLM; responses are marked with an `✦ AI` badge.
