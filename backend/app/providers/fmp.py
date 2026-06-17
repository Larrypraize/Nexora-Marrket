"""
Financial Modeling Prep (FMP) provider — quotes, movers, sectors, profile.
https://site.financialmodelingprep.com/developer/docs
"""
from typing import Optional

from ..config import settings
from ..http import fetch_json, ProviderError

BASE = "https://financialmodelingprep.com/api/v3"


def enabled() -> bool:
    return bool(settings.FMP_API_KEY)


async def quote(symbol: str) -> Optional[dict]:
    if not enabled():
        return None
    try:
        data = await fetch_json(
            "fmp", f"{BASE}/quote/{symbol.upper()}",
            params={"apikey": settings.FMP_API_KEY},
        )
        if not data:
            return None
        q = data[0]
        return {
            "symbol": q.get("symbol"),
            "name": q.get("name"),
            "price": q.get("price"),
            "change": q.get("change"),
            "change_percent": q.get("changesPercentage"),
            "high": q.get("dayHigh"),
            "low": q.get("dayLow"),
            "open": q.get("open"),
            "previous_close": q.get("previousClose"),
            "volume": q.get("volume"),
            "currency": "USD",
            "source": "fmp",
        }
    except (ProviderError, IndexError, KeyError):
        return None


async def movers(category: str) -> Optional[list]:
    """category: gainers | losers | active"""
    if not enabled():
        return None
    endpoint = {
        "gainers": "stock_market/gainers",
        "losers": "stock_market/losers",
        "active": "stock_market/actives",
        "trending": "stock_market/actives",
    }.get(category)
    if not endpoint:
        return None
    try:
        data = await fetch_json(
            "fmp", f"{BASE}/{endpoint}", params={"apikey": settings.FMP_API_KEY}
        )
        if not data:
            return None
        return [
            {
                "symbol": d.get("symbol"),
                "name": d.get("name"),
                "price": d.get("price"),
                "change_percent": d.get("changesPercentage"),
            }
            for d in data[:8]
        ]
    except ProviderError:
        return None


async def sectors() -> Optional[list]:
    if not enabled():
        return None
    try:
        data = await fetch_json(
            "fmp",
            "https://financialmodelingprep.com/api/v3/sectors-performance",
            params={"apikey": settings.FMP_API_KEY},
        )
        if not data:
            return None
        out = []
        for d in data:
            pct = d.get("changesPercentage", "0")
            if isinstance(pct, str):
                pct = float(pct.replace("%", "").strip() or 0)
            out.append({"sector": d.get("sector"), "change_percent": round(pct, 2)})
        return out or None
    except (ProviderError, ValueError):
        return None


async def profile(symbol: str) -> Optional[dict]:
    if not enabled():
        return None
    try:
        data = await fetch_json(
            "fmp", f"{BASE}/profile/{symbol.upper()}",
            params={"apikey": settings.FMP_API_KEY},
        )
        if not data:
            return None
        p = data[0]
        return {"name": p.get("companyName"), "currency": p.get("currency", "USD")}
    except (ProviderError, IndexError):
        return None
