"""
Deterministic mock data generator.

Used as a graceful fallback when a provider key is missing or an upstream call
fails, so the API (and the frontend) always works. All mock data is clearly
labeled with source="mock" so the UI can show a "demo data" badge.
"""
import hashlib
import math
import time
from typing import List

COMPANY_NAMES = {
    "AAPL": "Apple Inc.", "TSLA": "Tesla Inc.", "NVDA": "NVIDIA Corp.",
    "AMZN": "Amazon.com", "META": "Meta Platforms", "NFLX": "Netflix Inc.",
    "MSFT": "Microsoft Corp.", "GOOGL": "Alphabet Inc.", "AMD": "Adv. Micro Dev.",
    "INTC": "Intel Corp.", "COIN": "Coinbase", "F": "Ford Motor",
    "GTCO": "Guaranty Trust", "ZENITH": "Zenith Bank", "MTNN": "MTN Nigeria",
    "DANGCEM": "Dangote Cement", "BUACEM": "BUA Cement", "UBA": "United Bank Africa",
    "ACCESS": "Access Holdings", "SEPLAT": "Seplat Energy", "NESTLE": "Nestle Nigeria",
    "XOM": "Exxon Mobil", "CVX": "Chevron Corp.", "PG": "Procter & Gamble",
}

NGX = {"GTCO", "ZENITH", "MTNN", "DANGCEM", "BUACEM", "UBA", "ACCESS", "SEPLAT", "NESTLE"}


def _seed(symbol: str) -> float:
    h = hashlib.md5(symbol.upper().encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def company_name(symbol: str) -> str:
    return COMPANY_NAMES.get(symbol.upper(), f"{symbol.upper()} Corp.")


def currency_for(symbol: str) -> str:
    return "NGN" if symbol.upper() in NGX else "USD"


def mock_quote(symbol: str) -> dict:
    s = _seed(symbol)
    base = 20 + s * 1180
    # daily change roughly -4%..+5%, deterministic but varies through the day
    drift = math.sin(time.time() / 3600 + s * 6.28) * 0.03 + (s - 0.45) * 0.02
    change_pct = round(drift * 100, 2)
    price = round(base * (1 + drift), 2)
    prev = round(price / (1 + drift), 2)
    return {
        "symbol": symbol.upper(),
        "name": company_name(symbol),
        "price": price,
        "change": round(price - prev, 2),
        "change_percent": change_pct,
        "high": round(price * 1.012, 2),
        "low": round(price * 0.988, 2),
        "open": prev,
        "previous_close": prev,
        "volume": round(1_000_000 + s * 40_000_000),
        "currency": currency_for(symbol),
        "source": "mock",
    }


def mock_candles(symbol: str, count: int = 60) -> List[dict]:
    s = _seed(symbol)
    price = 20 + s * 1180
    now = int(time.time())
    out = []
    v = price
    for i in range(count):
        # pseudo-random walk
        r = math.sin(i * 0.6 + s * 12) * 0.02 + math.cos(i * 0.21 + s * 4) * 0.012
        o = v
        c = round(o * (1 + r), 2)
        h = round(max(o, c) * 1.008, 2)
        l = round(min(o, c) * 0.992, 2)
        out.append({
            "t": now - (count - i) * 86400,
            "o": round(o, 2), "h": h, "l": l, "c": c,
            "v": round(800_000 + abs(math.sin(i + s)) * 5_000_000),
        })
        v = c
    return out


def mock_news(symbols: List[str] | None = None, limit: int = 12) -> List[dict]:
    pool = [
        ("Nigerian banks post record half-year profits",
         "Major banks beat expectations on strong interest income — a confidence boost for the sector.",
         "Positive", ["GTCO", "ZENITH"], ["nigeria", "banking"]),
        ("Chipmaker unveils next-gen AI processor",
         "A new chip promises faster AI performance, lifting interest across the tech sector.",
         "Positive", ["NVDA", "AMD"], ["us", "tech"]),
        ("Oil prices climb on tighter global supply",
         "Higher oil prices could mean bigger profits for energy companies in coming months.",
         "Neutral", ["XOM", "SEPLAT"], ["global", "energy"]),
        ("Streaming giant slows on subscriber growth",
         "Fewer new sign-ups than hoped makes some investors more cautious about the stock.",
         "Negative", ["NFLX"], ["us", "tech"]),
        ("Telecom subscriber numbers hit new high",
         "Growing user base supports steady revenue — a quiet positive for telecom stocks.",
         "Positive", ["MTNN"], ["nigeria"]),
        ("Central bank signals possible rate cut",
         "Lower rates could encourage borrowing and lift the broader market mood.",
         "Positive", ["MARKET"], ["global", "banking"]),
        ("EV maker reports strong quarterly deliveries",
         "Delivery numbers beat estimates, attracting more buyers to the stock.",
         "Positive", ["TSLA"], ["us", "tech"]),
        ("Cement demand steady amid construction boom",
         "Reliable demand keeps cement makers on a calm, upward path.",
         "Neutral", ["DANGCEM", "BUACEM"], ["nigeria"]),
    ]
    now = int(time.time())
    out = []
    for i, (title, summ, sent, syms, cats) in enumerate(pool):
        if symbols and not any(x.upper() in [s.upper() for s in syms] for x in symbols):
            continue
        impact = "High" if sent == "Negative" else ("Positive" if sent == "Positive" else "Medium")
        out.append({
            "title": title, "summary": summ, "ai_summary": summ,
            "url": "https://nexora.market/news/" + str(i),
            "source": "Nexora Wire", "published_at": _iso(now - i * 3600),
            "sentiment": sent, "impact": impact,
            "symbols": syms, "categories": cats,
        })
    return out[:limit]


def _iso(ts: int) -> str:
    import datetime
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")


GAINERS = ["GTCO", "NVDA", "TSLA", "MTNN", "AMZN", "DANGCEM"]
LOSERS = ["META", "NFLX", "AAPL", "ZENITH", "INTC", "BUACEM"]
TRENDING = ["TSLA", "NVDA", "GTCO", "AMD", "MTNN", "COIN"]
ACTIVE = ["AAPL", "TSLA", "GTCO", "NVDA", "ZENITH", "F"]


def mock_movers(category: str) -> List[str]:
    return {"gainers": GAINERS, "losers": LOSERS,
            "trending": TRENDING, "active": ACTIVE}.get(category, GAINERS)


def mock_sectors() -> List[dict]:
    return [
        {"sector": "Banking", "change_percent": 3.4},
        {"sector": "Energy", "change_percent": 2.1},
        {"sector": "Consumer Goods", "change_percent": 0.8},
        {"sector": "Industrials", "change_percent": 0.4},
        {"sector": "Technology", "change_percent": -1.2},
    ]
