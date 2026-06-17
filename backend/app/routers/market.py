"""Market data endpoints: quotes, candles, movers, sectors, sentiment, overview."""
import asyncio
from fastapi import APIRouter, Query

from ..schemas import (
    Quote, CandleSeries, MoversResponse, SectorPerf, SentimentScore,
)
from ..services import market

router = APIRouter(prefix="/api/market", tags=["Market"])


@router.get("/quote/{symbol}", response_model=Quote)
async def quote(symbol: str):
    return await market.get_quote(symbol)


@router.get("/quotes", response_model=list[Quote])
async def quotes(symbols: str = Query(..., description="Comma-separated symbols")):
    syms = [s.strip() for s in symbols.split(",") if s.strip()][:25]
    return await asyncio.gather(*[market.get_quote(s) for s in syms])


@router.get("/candles/{symbol}", response_model=CandleSeries)
async def candles(symbol: str, count: int = Query(60, ge=10, le=200)):
    return await market.get_candles(symbol, count)


@router.get("/movers/{category}", response_model=MoversResponse)
async def movers(category: str):
    """category: gainers | losers | trending | active"""
    return await market.get_movers(category)


@router.get("/sectors", response_model=list[SectorPerf])
async def sectors():
    return await market.get_sectors()


@router.get("/sentiment", response_model=SentimentScore)
async def sentiment():
    return await market.get_market_sentiment()


@router.get("/overview")
async def overview():
    """Everything the homepage market section needs, in one call."""
    gainers, losers, trending, active, sectors_, sentiment_ = await asyncio.gather(
        market.get_movers("gainers"),
        market.get_movers("losers"),
        market.get_movers("trending"),
        market.get_movers("active"),
        market.get_sectors(),
        market.get_market_sentiment(),
    )
    return {
        "gainers": gainers,
        "losers": losers,
        "trending": trending,
        "active": active,
        "sectors": sectors_,
        "sentiment": sentiment_,
    }
