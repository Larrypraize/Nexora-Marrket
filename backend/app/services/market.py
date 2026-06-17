"""
Market aggregation service.

Orchestrates the five providers with a priority/fallback chain and caching:

  Quotes   : Finnhub -> Twelve Data -> FMP -> Alpha Vantage -> mock
  Candles  : Twelve Data -> Alpha Vantage -> Finnhub -> mock
  Movers   : FMP -> mock
  Sectors  : FMP -> mock
  News     : MarketAux -> Alpha Vantage -> Finnhub -> mock

Each layer returns None when unavailable, so we transparently fall through.
"""
import asyncio
from typing import Optional

from ..cache import cache
from ..config import settings
from ..providers import (
    alpha_vantage, finnhub, fmp, marketaux, mock, twelve_data,
)
from . import ai


# ----------------------------------------------------------------- quotes
async def get_quote(symbol: str) -> dict:
    symbol = symbol.upper()
    key = f"quote:{symbol}"

    async def factory():
        for fn in (finnhub.quote, twelve_data.quote, fmp.quote, alpha_vantage.quote):
            q = await fn(symbol)
            if q:
                # backfill name if missing
                if not q.get("name"):
                    q["name"] = await _resolve_name(symbol) or mock.company_name(symbol)
                return q
        return mock.mock_quote(symbol)

    return await cache.get_or_set(key, factory, ttl=settings.CACHE_TTL_SECONDS)


async def _resolve_name(symbol: str) -> Optional[str]:
    for fn in (fmp.profile, finnhub.profile):
        p = await fn(symbol)
        if p and p.get("name"):
            return p["name"]
    return None


# ----------------------------------------------------------------- candles
async def get_candles(symbol: str, count: int = 60) -> dict:
    symbol = symbol.upper()
    key = f"candles:{symbol}:{count}"

    async def factory():
        for fn in (
            lambda s: twelve_data.candles(s, outputsize=count),
            lambda s: alpha_vantage.daily_candles(s, limit=count),
            lambda s: finnhub.candles(s, days=count),
        ):
            c = await fn(symbol)
            if c:
                return {"symbol": symbol, "interval": "1day", "candles": c,
                        "source": c[0].get("source", "provider") if c else "provider"}
        return {"symbol": symbol, "interval": "1day",
                "candles": mock.mock_candles(symbol, count), "source": "mock"}

    return await cache.get_or_set(key, factory, ttl=settings.CACHE_TTL_SECONDS * 5)


# ----------------------------------------------------------------- movers
async def get_movers(category: str) -> dict:
    category = category.lower()
    key = f"movers:{category}"

    async def factory():
        rows = await fmp.movers(category)
        source = "fmp"
        if not rows:
            symbols = mock.mock_movers(category)
            rows = [{"symbol": s, "name": mock.company_name(s)} for s in symbols]
            source = "mock"

        items = []
        # enrich top items with quote + AI summary (bounded concurrency)
        rows = rows[:6]
        quotes = await asyncio.gather(*[get_quote(r["symbol"]) for r in rows])
        for r, q in zip(rows, quotes):
            chg = r.get("change_percent")
            if chg is None:
                chg = q.get("change_percent")
            score = ai.sentiment_score(chg)
            explanation, _ = await ai.explain_stock(
                r["symbol"], r.get("name") or q.get("name"), chg, score, None
            )
            items.append({
                "symbol": r["symbol"],
                "name": r.get("name") or q.get("name"),
                "price": r.get("price") or q.get("price"),
                "change_percent": chg,
                "sentiment": score,
                "ai_summary": explanation,
            })
        return {"category": category, "items": items, "source": source}

    return await cache.get_or_set(key, factory, ttl=settings.CACHE_TTL_SECONDS)


# ----------------------------------------------------------------- sectors
async def get_sectors() -> list[dict]:
    key = "sectors"

    async def factory():
        s = await fmp.sectors()
        return s or mock.mock_sectors()

    return await cache.get_or_set(key, factory, ttl=settings.CACHE_TTL_SECONDS * 5)


# ----------------------------------------------------------------- news
async def get_news(
    symbols: Optional[list[str]] = None,
    market: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 12,
) -> dict:
    key = f"news:{','.join(symbols or [])}:{market}:{category}:{limit}"

    async def factory():
        rows = await marketaux.news(symbols=symbols, market=market, limit=limit)
        source = "marketaux"
        if not rows and symbols:
            rows = await alpha_vantage.news_sentiment(symbols[0], limit=limit)
            source = "alpha_vantage"
        if not rows and symbols:
            rows = await finnhub.company_news(symbols[0], limit=limit)
            source = "finnhub"
        if not rows:
            rows = mock.mock_news(symbols=symbols, limit=limit)
            source = "mock"

        # category filter (client-side)
        if category and category not in ("all", None):
            rows = [r for r in rows if category.lower() in
                    [c.lower() for c in (r.get("categories") or [])]] or rows

        # ensure each has an ai_summary in plain language
        for r in rows:
            if not r.get("ai_summary"):
                r["ai_summary"] = r.get("summary") or r.get("title")
        return {"articles": rows[:limit], "source": source}

    return await cache.get_or_set(key, factory, ttl=settings.CACHE_TTL_SECONDS * 3)


# ----------------------------------------------------------------- market sentiment
async def get_market_sentiment() -> dict:
    """Aggregate sentiment from current gainers/losers spread."""
    key = "market:sentiment"

    async def factory():
        gainers = await get_movers("gainers")
        losers = await get_movers("losers")
        g_avg = _avg([i.get("change_percent") for i in gainers["items"]])
        l_avg = _avg([i.get("change_percent") for i in losers["items"]])
        net = (g_avg + l_avg) / 2 if (g_avg or l_avg) else 0
        score = ai.sentiment_score(net)
        label = ai.sentiment_label(score)
        summary = {
            "Bullish": "Overall investor mood is optimistic. Buying activity is "
                       "stronger than selling across most major sectors.",
            "Neutral": "The market mood is balanced today. Buyers and sellers are "
                       "fairly evenly matched.",
            "Bearish": "Investors are cautious today. Selling is a little stronger "
                       "than buying across the market.",
        }[label]
        return {"score": score, "label": label, "summary": summary}

    return await cache.get_or_set(key, factory, ttl=settings.CACHE_TTL_SECONDS)


def _avg(vals) -> float:
    nums = [v for v in vals if isinstance(v, (int, float))]
    return sum(nums) / len(nums) if nums else 0.0


# ----------------------------------------------------------------- full analysis
async def analyze(symbol: str) -> dict:
    symbol = symbol.upper()
    quote, candle_data, news_data = await asyncio.gather(
        get_quote(symbol),
        get_candles(symbol, 60),
        get_news(symbols=[symbol], limit=4),
    )
    chg = quote.get("change_percent")
    # derive dominant news sentiment
    sentiments = [a.get("sentiment") for a in news_data["articles"] if a.get("sentiment")]
    news_tone = None
    if sentiments:
        pos = sentiments.count("Positive")
        neg = sentiments.count("Negative")
        news_tone = "Positive" if pos > neg else ("Negative" if neg > pos else "Neutral")

    score = ai.sentiment_score(chg, news_tone)
    label = ai.sentiment_label(score)
    trend = ai.trend_from_change(chg)
    risk_word, risk_level = ai.risk_from_volatility(
        chg, quote.get("high"), quote.get("low"), quote.get("price")
    )
    explanation, ai_powered = await ai.explain_stock(
        symbol, quote.get("name"), chg, score, news_tone
    )

    return {
        "symbol": symbol,
        "name": quote.get("name"),
        "quote": quote,
        "trend": trend,
        "sentiment": {"score": score, "label": label,
                      "summary": ai.rule_explanation(symbol, quote.get("name"), chg, score, news_tone)},
        "risk_rating": risk_word,
        "risk_level": risk_level,
        "explanation": explanation,
        "news": news_data["articles"],
        "candles": candle_data["candles"][-60:],
        "ai_powered": ai_powered,
    }


# ----------------------------------------------------------------- insights
async def get_insights() -> list[dict]:
    """Generate dynamic AI insight cards from sector + movers data."""
    key = "insights"

    async def factory():
        sectors = await get_sectors()
        cards = []
        sorted_sectors = sorted(sectors, key=lambda s: s["change_percent"], reverse=True)
        for s in sorted_sectors[:2]:  # strongest
            cards.append(_insight_from_sector(s, bull=True))
        for s in sorted_sectors[-2:]:  # weakest
            if s["change_percent"] < 0.5:
                cards.append(_insight_from_sector(s, bull=False))
        return cards[:4]

    return await cache.get_or_set(key, factory, ttl=settings.CACHE_TTL_SECONDS * 3)


def _insight_from_sector(s: dict, bull: bool) -> dict:
    pct = s["change_percent"]
    sector = s["sector"]
    direction = "bull" if pct > 0.5 else ("bear" if pct < -0.5 else "neu")
    conf = int(min(95, 55 + abs(pct) * 9))
    if direction == "bull":
        text = (f"The {sector} sector is gaining momentum ({pct:+.1f}%). More "
                f"investors are moving money into these stocks, a sign of growing "
                f"confidence.")
    elif direction == "bear":
        text = (f"The {sector} sector is under pressure ({pct:+.1f}%). Some investors "
                f"are pulling back, so the mood here has cooled this week.")
    else:
        text = (f"The {sector} sector is steady ({pct:+.1f}%). Growth is slow but "
                f"reliable, with no big surprises for investors.")
    return {
        "title": f"{sector} sector {'gaining momentum' if direction=='bull' else 'showing weaker sentiment' if direction=='bear' else 'showing steady growth'}",
        "direction": direction,
        "explanation": text,
        "confidence": conf,
        "related": _sector_symbols(sector),
    }


def _sector_symbols(sector: str) -> list[str]:
    mapping = {
        "Banking": ["GTCO", "ZENITH", "UBA"],
        "Technology": ["NVDA", "AAPL", "META"],
        "Energy": ["XOM", "SEPLAT", "CVX"],
        "Consumer Goods": ["NESTLE", "PG", "DANGCEM"],
        "Industrials": ["DANGCEM", "BUACEM"],
    }
    return mapping.get(sector, [])
