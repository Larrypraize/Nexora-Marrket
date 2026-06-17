"""
MarketAux provider — financial news with entity + sentiment data.
https://www.marketaux.com/documentation
"""
from typing import Optional

from ..config import settings
from ..http import fetch_json, ProviderError

BASE = "https://api.marketaux.com/v1"


def enabled() -> bool:
    return bool(settings.MARKETAUX_API_KEY)


def _map_country(market_filter: str | None) -> Optional[str]:
    return {
        "nigeria": "ng", "us": "us", "global": None,
    }.get((market_filter or "").lower())


async def news(
    symbols: list[str] | None = None,
    market: str | None = None,
    limit: int = 12,
) -> Optional[list]:
    if not enabled():
        return None
    params = {
        "api_token": settings.MARKETAUX_API_KEY,
        "language": "en",
        "limit": min(limit, 50),
        "filter_entities": "true",
    }
    if symbols:
        params["symbols"] = ",".join(s.upper() for s in symbols)
    country = _map_country(market)
    if country:
        params["countries"] = country
    try:
        data = await fetch_json("marketaux", f"{BASE}/news/all", params=params)
        articles = (data or {}).get("data")
        if not articles:
            return None
        out = []
        for a in articles[:limit]:
            entities = a.get("entities", [])
            syms = [e.get("symbol") for e in entities if e.get("symbol")][:4]
            # average entity sentiment -> label
            scores = [e.get("sentiment_score") for e in entities
                      if isinstance(e.get("sentiment_score"), (int, float))]
            avg = sum(scores) / len(scores) if scores else 0.0
            sentiment = ("Positive" if avg > 0.15 else
                         "Negative" if avg < -0.15 else "Neutral")
            impact = "High" if abs(avg) > 0.4 else ("Positive" if avg > 0 else "Medium")
            out.append({
                "title": a.get("title"),
                "summary": a.get("description") or a.get("snippet"),
                "url": a.get("url"),
                "source": a.get("source"),
                "published_at": a.get("published_at"),
                "sentiment": sentiment,
                "impact": impact,
                "symbols": syms,
                "categories": [],
            })
        return out or None
    except ProviderError:
        return None
