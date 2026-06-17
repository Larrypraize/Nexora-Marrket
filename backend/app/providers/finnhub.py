"""
Finnhub provider — real-time quotes, company profile, candles.
https://finnhub.io/docs/api
"""
import time
from typing import Optional

from ..config import settings
from ..http import fetch_json, ProviderError

BASE = "https://finnhub.io/api/v1"


def enabled() -> bool:
    return bool(settings.FINNHUB_API_KEY)


async def quote(symbol: str) -> Optional[dict]:
    if not enabled():
        return None
    try:
        data = await fetch_json(
            "finnhub", f"{BASE}/quote",
            params={"symbol": symbol.upper(), "token": settings.FINNHUB_API_KEY},
        )
        if not data or data.get("c") in (None, 0):
            return None
        prev = data.get("pc")
        price = data.get("c")
        return {
            "symbol": symbol.upper(),
            "price": price,
            "change": data.get("d"),
            "change_percent": data.get("dp"),
            "high": data.get("h"),
            "low": data.get("l"),
            "open": data.get("o"),
            "previous_close": prev,
            "currency": "USD",
            "source": "finnhub",
        }
    except ProviderError:
        return None


async def profile(symbol: str) -> Optional[dict]:
    if not enabled():
        return None
    try:
        data = await fetch_json(
            "finnhub", f"{BASE}/stock/profile2",
            params={"symbol": symbol.upper(), "token": settings.FINNHUB_API_KEY},
        )
        if not data:
            return None
        return {"name": data.get("name"), "currency": data.get("currency", "USD")}
    except ProviderError:
        return None


async def candles(symbol: str, days: int = 60) -> Optional[list]:
    """Finnhub stock candles (note: requires paid tier for some symbols)."""
    if not enabled():
        return None
    try:
        now = int(time.time())
        data = await fetch_json(
            "finnhub", f"{BASE}/stock/candle",
            params={
                "symbol": symbol.upper(), "resolution": "D",
                "from": now - days * 86400, "to": now,
                "token": settings.FINNHUB_API_KEY,
            },
        )
        if not data or data.get("s") != "ok":
            return None
        out = []
        for i in range(len(data["c"])):
            out.append({
                "t": data["t"][i], "o": data["o"][i], "h": data["h"][i],
                "l": data["l"][i], "c": data["c"][i], "v": data["v"][i],
            })
        return out or None
    except ProviderError:
        return None


async def company_news(symbol: str, limit: int = 8) -> Optional[list]:
    if not enabled():
        return None
    try:
        import datetime
        today = datetime.date.today()
        frm = today - datetime.timedelta(days=14)
        data = await fetch_json(
            "finnhub", f"{BASE}/company-news",
            params={
                "symbol": symbol.upper(),
                "from": frm.isoformat(), "to": today.isoformat(),
                "token": settings.FINNHUB_API_KEY,
            },
        )
        if not data:
            return None
        out = []
        for a in data[:limit]:
            out.append({
                "title": a.get("headline"),
                "summary": a.get("summary"),
                "url": a.get("url"),
                "source": a.get("source"),
                "published_at": _iso(a.get("datetime")),
                "symbols": [symbol.upper()],
                "categories": [a.get("category", "")],
            })
        return out or None
    except ProviderError:
        return None


def _iso(ts) -> Optional[str]:
    if not ts:
        return None
    import datetime
    return datetime.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%dT%H:%M:%SZ")
