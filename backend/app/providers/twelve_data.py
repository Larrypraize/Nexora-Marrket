"""
Twelve Data provider — quotes and time-series candles.
https://twelvedata.com/docs
"""
from typing import Optional

from ..config import settings
from ..http import fetch_json, ProviderError

BASE = "https://api.twelvedata.com"


def enabled() -> bool:
    return bool(settings.TWELVE_DATA_API_KEY)


async def quote(symbol: str) -> Optional[dict]:
    if not enabled():
        return None
    try:
        data = await fetch_json(
            "twelve_data", f"{BASE}/quote",
            params={"symbol": symbol.upper(), "apikey": settings.TWELVE_DATA_API_KEY},
        )
        if not data or data.get("status") == "error" or "close" not in data:
            return None
        return {
            "symbol": data.get("symbol", symbol.upper()),
            "name": data.get("name"),
            "price": _f(data.get("close")),
            "change": _f(data.get("change")),
            "change_percent": _f(data.get("percent_change")),
            "high": _f(data.get("high")),
            "low": _f(data.get("low")),
            "open": _f(data.get("open")),
            "previous_close": _f(data.get("previous_close")),
            "volume": _f(data.get("volume")),
            "currency": data.get("currency", "USD"),
            "source": "twelve_data",
        }
    except ProviderError:
        return None


async def candles(symbol: str, outputsize: int = 60, interval: str = "1day") -> Optional[list]:
    if not enabled():
        return None
    try:
        data = await fetch_json(
            "twelve_data", f"{BASE}/time_series",
            params={
                "symbol": symbol.upper(), "interval": interval,
                "outputsize": outputsize, "apikey": settings.TWELVE_DATA_API_KEY,
            },
        )
        values = (data or {}).get("values")
        if not values:
            return None
        import datetime
        out = []
        for v in reversed(values):  # API returns newest-first
            ts = int(datetime.datetime.strptime(
                v["datetime"], "%Y-%m-%d" if len(v["datetime"]) == 10 else "%Y-%m-%d %H:%M:%S"
            ).timestamp())
            out.append({
                "t": ts, "o": _f(v["open"]), "h": _f(v["high"]),
                "l": _f(v["low"]), "c": _f(v["close"]), "v": _f(v.get("volume", 0)) or 0,
            })
        return out or None
    except (ProviderError, KeyError, ValueError):
        return None


def _f(v) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
