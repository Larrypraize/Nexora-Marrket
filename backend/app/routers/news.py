"""News endpoints with market/category/symbol filters."""
from fastapi import APIRouter, Query
from typing import Optional

from ..schemas import NewsResponse
from ..services import market

router = APIRouter(prefix="/api/news", tags=["News"])


@router.get("", response_model=NewsResponse)
async def news(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols"),
    market_filter: Optional[str] = Query(
        None, alias="market", description="nigeria | us | global"
    ),
    category: Optional[str] = Query(
        None, description="banking | tech | energy | consumer | all"
    ),
    limit: int = Query(12, ge=1, le=50),
):
    syms = [s.strip() for s in symbols.split(",")] if symbols else None
    return await market.get_news(
        symbols=syms, market=market_filter, category=category, limit=limit
    )
