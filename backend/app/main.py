"""
NEXORA MARKET — FastAPI application entrypoint.

AI-powered market intelligence backend aggregating five data providers
(MarketAux, Finnhub, FMP, Alpha Vantage, Twelve Data) behind a single API,
with auth, watchlists, caching and a pluggable AI explanation layer.
"""
import logging
from contextlib import asynccontextmanager

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from .http import close_client
from .routers import auth, intelligence, market, news, watchlist

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("nexora")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    status = settings.provider_status()
    active = [k for k, v in status.items() if v]
    logger.info("NEXORA MARKET API starting. Active providers: %s",
                ", ".join(active) if active else "none (mock mode)")
    yield
    await close_client()
    logger.info("NEXORA MARKET API shut down cleanly.")


app = FastAPI(
    title="NEXORA MARKET API",
    description=(
        "AI-powered market intelligence. Aggregates MarketAux, Finnhub, FMP, "
        "Alpha Vantage and Twelve Data. Provides quotes, candles, movers, "
        "sectors, news, sentiment, plain-language AI analysis, an AI assistant, "
        "user auth and watchlists.\n\n"
        "**Educational market intelligence only — not financial advice.**"
    ),
    version="1.0.0",
    lifespan=lifespan,
    contact={"name": "Nexora Market", "url": "https://nexora.market"},
    license_info={"name": "Proprietary"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": request.url.path},
    )


# ---- Routers ----
app.include_router(market.router)
app.include_router(news.router)
app.include_router(intelligence.router)
app.include_router(auth.router)
app.include_router(watchlist.router)


# ---- Meta endpoints ----
@app.get("/api", tags=["Meta"])
async def api_root():
    return {
        "name": "NEXORA MARKET API",
        "tagline": "AI Market Intelligence",
        "version": "1.0.0",
        "docs": "/docs",
        "website": "/",
        "disclaimer": ("Nexora Market provides market intelligence and educational "
                       "information only. It does not provide financial or "
                       "investment advice."),
    }


@app.get("/health", tags=["Meta"])
async def health():
    return {
        "status": "ok",
        "providers": settings.provider_status(),
        "ai_mode": "llm" if settings.llm_enabled else "rule-based",
        "env": settings.ENV,
    }


# ---- Serve the frontend website ----
# The project root (contains index.html and assets/) sits two levels up
# from this file: backend/app/main.py -> backend/ -> <project root>.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_INDEX_HTML = os.path.join(_PROJECT_ROOT, "index.html")
_ASSETS_DIR = os.path.join(_PROJECT_ROOT, "assets")

if os.path.isdir(_ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=_ASSETS_DIR), name="assets")


@app.get("/", include_in_schema=False)
async def serve_website():
    if os.path.isfile(_INDEX_HTML):
        return FileResponse(_INDEX_HTML, media_type="text/html")
    return JSONResponse({"detail": "index.html not found", "api": "/api"}, status_code=404)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    fav = os.path.join(_ASSETS_DIR, "favicon.png")
    if os.path.isfile(fav):
        return FileResponse(fav, media_type="image/png")
    return JSONResponse({"detail": "no favicon"}, status_code=404)
