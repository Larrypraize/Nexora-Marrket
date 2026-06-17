"""Watchlist endpoints with free/premium plan limits."""
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import User, WatchlistItem, get_db
from ..schemas import WatchlistAdd, WatchlistItemOut
from ..services import auth, market

router = APIRouter(prefix="/api/watchlist", tags=["Watchlist"])


def _item_dict(i: WatchlistItem) -> dict:
    return {
        "id": i.id,
        "symbol": i.symbol,
        "name": i.name,
        "created_at": i.created_at.isoformat() if i.created_at else "",
    }


@router.get("", response_model=list[WatchlistItemOut])
async def list_watchlist(
    current: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)
):
    rows = await db.scalars(
        select(WatchlistItem).where(WatchlistItem.user_id == current.id)
        .order_by(WatchlistItem.created_at)
    )
    return [_item_dict(i) for i in rows]


@router.get("/quotes")
async def watchlist_with_quotes(
    current: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)
):
    """Watchlist enriched with live quotes for the dashboard."""
    rows = list(await db.scalars(
        select(WatchlistItem).where(WatchlistItem.user_id == current.id)
        .order_by(WatchlistItem.created_at)
    ))
    quotes = await asyncio.gather(*[market.get_quote(i.symbol) for i in rows]) if rows else []
    return [{**_item_dict(i), "quote": q} for i, q in zip(rows, quotes)]


@router.post("", response_model=WatchlistItemOut, status_code=201)
async def add_item(
    payload: WatchlistAdd,
    current: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    symbol = payload.symbol.upper().strip()
    # dedupe first
    existing = await db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.user_id == current.id, WatchlistItem.symbol == symbol
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already in watchlist")
    # plan limit enforcement
    count = len(list(await db.scalars(
        select(WatchlistItem).where(WatchlistItem.user_id == current.id)
    )))
    if current.plan == "free" and count >= settings.FREE_WATCHLIST_LIMIT:
        raise HTTPException(
            status_code=403,
            detail=f"Free plan is limited to {settings.FREE_WATCHLIST_LIMIT} stocks. "
                   "Upgrade to Premium for unlimited watchlists.",
        )

    name = payload.name
    if not name:
        q = await market.get_quote(symbol)
        name = q.get("name")
    item = WatchlistItem(user_id=current.id, symbol=symbol, name=name)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _item_dict(item)


@router.delete("/{symbol}", status_code=204)
async def remove_item(
    symbol: str,
    current: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        delete(WatchlistItem).where(
            WatchlistItem.user_id == current.id,
            WatchlistItem.symbol == symbol.upper().strip(),
        )
    )
    await db.commit()
    return None
