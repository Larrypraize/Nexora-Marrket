"""
Alpha Vantage provider — quotes, daily series, news+sentiment.
https://www.alphavantage.co/documentation/
Note: free tier is limited to ~25 requests/day, so results are cached hard.
"""
from typing import Optional

from ..config import settings
from ..http import fetch_json, ProviderError

BASE = "https://www.alphavantage.co/query"


def enabled() -> bool:
    return bool(settings.ALPHA_VANTAGE_API_KEY)


async def quote(symbol: str) -> Optional[dict]:
    if not enabled():
        return None
    try:
        data = await fetch_json(
            "alpha_vantage", BASE,
            params={
                "function": "GLOBAL_QUOTE", "symbol": symbol.upper(),
                "apikey": settings.ALPHA_VANTAGE_API_KEY,
            },
        )
        q = (data or {}).get("Global Quote") or {}
        if not q or not q.get("05. price"):
            return None
        pct = q.get("10. change percent", "0%").replace("%", "")
        return {
            "symbol": q.get("01. symbol", symbol.upper()),
            "price": _f(q.get("05. price")),
            "change": _f(q.get("09. change")),
            "change_percent": _f(pct),
            "high": _f(q.get("03. high")),
            "low": _f(q.get("04. low")),
            "open": _f(q.get("02. open")),
            "previous_close": _f(q.get("08. previous close")),
            "volume": _f(q.get("06. volume")),
            "currency": "USD",
            "source": "alpha_vantage",
        }
    except ProviderError:
        return None


async def daily_candles(symbol: str, limit: int = 60) -> Optional[list]:
    if not enabled():
        return None
    try:
        data = await fetch_json(
            "alpha_vantage", BASE,
            params={
                "function": "TIME_SERIES_DAILY", "symbol": symbol.upper(),
                "outputsize": "compact", "apikey": settings.ALPHA_VANTAGE_API_KEY,
            },
        )
        series = (data or {}).get("Time Series (Daily)")
        if not series:
            return None
        import datetime
        out = []
        for day, vals in sorted(series.items())[-limit:]:
            ts = int(datetime.datetime.strptime(day, "%Y-%m-%d").timestamp())
            out.append({
                "t": ts, "o": _f(vals["1. open"]), "h": _f(vals["2. high"]),
                "l": _f(vals["3. low"]), "c": _f(vals["4. close"]),
                "v": _f(vals["5. volume"]),
            })
        return out or None
    except (ProviderError, KeyError):
        return None


async def news_sentiment(symbol: str, limit: int = 8) -> Optional[list]:
    if not enabled():
        return None
    try:
        data = await fetch_json(
            "alpha_vantage", BASE,
            params={
                "function": "NEWS_SENTIMENT", "tickers": symbol.upper(),
                "limit": limit, "apikey": settings.ALPHA_VANTAGE_API_KEY,
            },
        )
        feed = (data or {}).get("feed")
        if not feed:
            return None
        out = []
        for a in feed[:limit]:
            label = a.get("overall_sentiment_label", "Neutral")
            sentiment = ("Positive" if "Bullish" in label
                         else "Negative" if "Bearish" in label else "Neutral")
            out.append({
                "title": a.get("title"),
                "summary": a.get("summary"),
                "url": a.get("url"),
                "source": a.get("source"),
                "published_at": a.get("time_published"),
                "sentiment": sentiment,
                "symbols": [t.get("ticker") for t in a.get("ticker_sentiment", [])][:4],
                "categories": [t.get("topic") for t in a.get("topics", [])][:3],
            })
        return out or None
    except ProviderError:
        return None


def _f(v) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
