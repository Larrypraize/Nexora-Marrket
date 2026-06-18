"""
AI explanation engine.

Two layers:
  1) Rule-based generator — always available, deterministic, beginner-friendly.
  2) Optional LLM layer — used when LLM_API_KEY is set (OpenAI-compatible).
     Falls back to the rule-based engine on any error.

Design principle (per product brief): NEVER show jargon. Translate technical
signals into plain language a beginner understands.
"""
import logging
from typing import Optional

from ..config import settings
from ..http import get_client

logger = logging.getLogger("nexora.ai")

SYSTEM_PROMPT = (
    "You are Nexora, an AI market-intelligence assistant. You explain stocks, "
    "trends and market movements in SIMPLE, plain language for people with little "
    "or no financial knowledge. Never use jargon like 'RSI', 'MACD' or 'bullish "
    "divergence'. Instead say things like 'buying pressure is increasing' or "
    "'investors appear more confident'. Be concise (2-5 sentences), friendly and "
    "neutral. Always include a brief, clear takeaway. You provide educational "
    "market intelligence ONLY — never financial or investment advice."
)


# ---------------------------------------------------------------- rule-based
def trend_from_change(change_pct: Optional[float]) -> str:
    if change_pct is None:
        return "Sideways"
    if change_pct >= 3:
        return "Strong Upward"
    if change_pct >= 0.5:
        return "Upward"
    if change_pct <= -3:
        return "Strong Downward"
    if change_pct <= -0.5:
        return "Downward"
    return "Sideways"


def sentiment_score(change_pct: Optional[float], news_sentiment: Optional[str] = None) -> int:
    """Combine price action + news into a 0-100 confidence score."""
    base = 50
    if change_pct is not None:
        base += max(min(change_pct * 6, 35), -35)
    if news_sentiment == "Positive":
        base += 8
    elif news_sentiment == "Negative":
        base -= 8
    return int(max(2, min(98, base)))


def sentiment_label(score: int) -> str:
    if score >= 66:
        return "Bullish"
    if score >= 45:
        return "Neutral"
    return "Bearish"


def risk_from_volatility(change_pct: Optional[float], high=None, low=None, price=None) -> tuple[str, int]:
    """Estimate a simple 1-5 risk level from intraday range + move size."""
    score = 2
    if change_pct is not None and abs(change_pct) > 3:
        score += 1
    if high and low and price:
        rng = (high - low) / price if price else 0
        if rng > 0.04:
            score += 1
        if rng > 0.07:
            score += 1
    score = max(1, min(5, score))
    word = "Low" if score <= 2 else ("Moderate" if score == 3 else "High")
    return word, score


def rule_explanation(symbol: str, name: str, change_pct: Optional[float],
                     score: int, news_sentiment: Optional[str] = None) -> str:
    label = sentiment_label(score)
    nm = name or symbol
    if change_pct is None:
        return (f"{nm} is trading steadily today. Overall investor sentiment is "
                f"{label.lower()} ({score}/100). There are no dramatic moves right now.")
    direction = "rising" if change_pct > 0.3 else ("falling" if change_pct < -0.3 else "holding steady")
    if change_pct > 0.3:
        driver = ("more investors are buying than selling, which usually means "
                  "growing confidence in the company")
    elif change_pct < -0.3:
        driver = ("more investors are selling than buying, often to lock in profits "
                  "or out of short-term caution")
    else:
        driver = "buyers and sellers are fairly balanced, so the price is calm"
    extra = ""
    if news_sentiment == "Positive":
        extra = " Recent news around the stock has been mostly positive, supporting the mood."
    elif news_sentiment == "Negative":
        extra = " Some recent news has been negative, which is weighing on the mood."
    return (f"{nm} is {direction} ({change_pct:+.2f}% today). In simple terms, "
            f"{driver}. Overall sentiment is {label.lower()} at {score}/100.{extra}")


# ---------------------------------------------------------------- LLM layer
async def llm_complete(messages: list[dict]) -> Optional[str]:
    """Call an OpenAI-compatible chat endpoint. Returns None on failure."""
    if not settings.llm_enabled:
        return None
    try:
        client = get_client()
        resp = await client.post(
            f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
            json={
                "model": settings.LLM_MODEL,
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 320,
            },
            timeout=25.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:  # noqa: BLE001 - never let AI failure break the API
        logger.warning("LLM call failed, using rule-based fallback: %s", e)
        return None


async def explain_stock(symbol: str, name: str, change_pct, score, news_sentiment,
                        context: str = "") -> tuple[str, bool]:
    """Return (explanation, ai_powered)."""
    if settings.llm_enabled:
        prompt = (
            f"Explain stock {symbol} ({name}) for a beginner. "
            f"Today's change: {change_pct}%. Sentiment score: {score}/100. "
            f"Recent news tone: {news_sentiment or 'mixed'}. {context} "
            "Give a clear 2-4 sentence plain-language explanation."
        )
        out = await llm_complete([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        if out:
            return out, True
    return rule_explanation(symbol, name, change_pct, score, news_sentiment), False


async def chat_reply(message: str, history: list[dict],
                     context: str = "") -> tuple[str, bool]:
    """Conversational assistant. Returns (reply, ai_powered).

    `context` is live market data (quotes/sentiment/movers) injected by the
    router so the AI answers with REAL numbers instead of guessing.
    """
    if settings.llm_enabled:
        system = SYSTEM_PROMPT
        if context:
            system += ("\n\nUse ONLY the following live market data to answer. "
                       "If the data doesn't contain the answer, say you don't have "
                       "that figure right now.\n\n=== LIVE MARKET DATA ===\n" + context)
        msgs = [{"role": "system", "content": system}]
        msgs += [{"role": m["role"], "content": m["content"]} for m in history[-8:]]
        msgs.append({"role": "user", "content": message})
        out = await llm_complete(msgs)
        if out:
            return out, True
    return _rule_chat(message, context), False


def _rule_chat(message: str, context: str = "") -> str:
    # If we have live data context, lead with it (keeps answers accurate).
    if context:
        return (context.strip() + "\n\nIn simple terms: this reflects today's "
                "live market activity. (Educational info only — not financial advice.)")
    m = message.lower()
    if "gtco" in m:
        return ("GTCO is currently attracting strong interest. Buying pressure is "
                "increasing and investors appear more confident, often after solid "
                "bank earnings. Sentiment looks bullish. (Educational info only.)")
    if "tesla" in m or "tsla" in m:
        return ("Tesla tends to move a lot day-to-day. When it rises, it's usually "
                "because more investors are buying on positive news like strong "
                "deliveries. Keep in mind its price can swing quickly, so risk is "
                "moderate. (Educational info only.)")
    if "nvidia" in m or "nvda" in m:
        return ("NVIDIA is one of the most-watched stocks thanks to huge demand for "
                "AI chips. Investor excitement is high, though prices can swing a "
                "lot. (Educational info only.)")
    if "sector" in m:
        return ("Right now banking and energy sectors look strongest, helped by "
                "earnings and higher commodity prices. Technology is softer this "
                "week as some investors take profits. (Educational info only.)")
    if "down" in m or "drop" in m or "fall" in m:
        return ("When the market dips, it usually means more investors are selling "
                "than buying for a short period — often to lock in gains or out of "
                "caution. A small dip after a strong run is normal. (Educational "
                "info only.)")
    if "attention" in m or "trending" in m or "active" in m:
        return ("The most talked-about names today include NVDA and TSLA (AI buzz), "
                "GTCO (bank earnings) and COIN (crypto strength). (Educational info "
                "only.)")
    return ("Great question! To understand any stock, look at three simple things: "
            "the recent price trend, whether investors feel confident or nervous "
            "(sentiment), and the latest news. Ask me about a specific stock like "
            "'Analyze Apple' and I'll break it down in plain language. (Educational "
            "info only.)")
