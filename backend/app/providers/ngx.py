"""
NGX Pulse provider — Nigerian Exchange (NGX) market data.
https://ngxpulse.ng/api

Free "Personal" tier: 10 req/min, 100 req/day. We cache hard to stay within it.
Covers 150+ NGX equities: price, % change, volume, market cap, sector + the
market overview (ASI, advancers/decliners, top gainers/losers).

Auth: pass your key in the `X-API-Key` header (env: NGX_API_KEY).
"""
from typing import Optional

from ..config import settings
from ..http import fetch_json, ProviderError

BASE = "https://www.ngxpulse.ng/api/ngxdata"

# Common NGX tickers (so we can detect "this is a Nigerian stock" and route it
# to NGX Pulse). Symbols on NGX are alphabetic, e.g. GTCO, DANGCEM, MTNN.
KNOWN_NGX = {
    "GTCO", "ZENITHBANK", "ZENITH", "UBA", "ACCESSCORP", "ACCESS", "FBNH",
    "MTNN", "AIRTELAFRI", "DANGCEM", "BUACEMENT", "BUACEM", "WAPCO", "DANGSUGAR",
    "NESTLE", "NB", "GUINNESS", "FLOURMILL", "SEPLAT", "TOTAL", "CONOIL",
    "OANDO", "ARADEL", "TRANSCORP", "BUAFOODS", "PRESCO", "OKOMUOIL",
    "STANBIC", "FCMB", "FIDELITYBK", "STERLINGNG", "WEMABANK", "JAIZBANK",
    "ETERNA", "CADBURY", "UNILEVER", "PZ", "VITAFOAM", "CUTIX", "BERGER",
    "CWG", "CHAMS", "NGXGROUP", "CORNERST", "AIICO", "CUSTODIAN", "WAPIC",
    "TRANSCOHOT", "GEREGU", "TRANSPOWER", "JBERGER", "LIVESTOCK", "ELLAHLAKES",
}

# normalise common aliases to the symbols NGX Pulse expects
ALIASES = {
    "ZENITH": "ZENITHBANK",
    "ACCESS": "ACCESSCORP",
    "BUACEM": "BUACEMENT",
    "TOTAL": "TOTALNG",
}


def enabled() -> bool:
    return bool(settings.NGX_API_KEY)


def _headers() -> dict:
    return {"X-API-Key": settings.NGX_API_KEY, "Content-Type": "application/json"}


def is_ngx_symbol(symbol: str) -> bool:
    s = symbol.upper().strip()
    return s in KNOWN_NGX or s in ALIASES


def canonical(symbol: str) -> str:
    s = symbol.upper().strip()
    return ALIASES.get(s, s)


def _to_quote(d: dict) -> dict:
    return {
        "symbol": d.get("symbol"),
        "name": d.get("name"),
        "price": d.get("current_price"),
        "change": None,
        "change_percent": d.get("change_percent"),
        "high": None,
        "low": None,
        "open": None,
        "previous_close": None,
        "volume": d.get("volume"),
        "currency": "NGN",
        "sector": d.get("sector"),
        "source": "ngx_pulse",
    }


async def quote(symbol: str) -> Optional[dict]:
    if not enabled():
        return None
    sym = canonical(symbol)
    try:
        d = await fetch_json("ngx_pulse", f"{BASE}/prices/{sym}", headers=_headers())
        if not d or d.get("current_price") is None:
            return None
        return _to_quote(d)
    except ProviderError:
        return None


async def all_stocks() -> Optional[list]:
    """Full list of 150+ NGX equities (cached upstream by caller)."""
    if not enabled():
        return None
    try:
        data = await fetch_json("ngx_pulse", f"{BASE}/stocks", headers=_headers())
        if not data or not isinstance(data, list):
            return None
        return [_to_quote(d) for d in data if d.get("current_price") is not None]
    except ProviderError:
        return None


async def market_overview() -> Optional[dict]:
    """ASI + breadth + top gainers/losers."""
    if not enabled():
        return None
    try:
        d = await fetch_json("ngx_pulse", f"{BASE}/market", headers=_headers())
        if not d:
            return None
        return d
    except ProviderError:
        return None
