"""Pydantic response/request models shared across routers."""
from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr, Field


# ---------- Market data ----------
class Quote(BaseModel):
    symbol: str
    name: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    previous_close: Optional[float] = None
    volume: Optional[float] = None
    currency: str = "USD"
    source: str = "mock"


class Candle(BaseModel):
    t: int  # unix seconds
    o: float
    h: float
    l: float
    c: float
    v: float = 0


class CandleSeries(BaseModel):
    symbol: str
    interval: str
    candles: List[Candle]
    source: str = "mock"


class SentimentScore(BaseModel):
    score: int = Field(ge=0, le=100)          # 0 bearish .. 100 bullish
    label: Literal["Bearish", "Neutral", "Bullish"]
    summary: str


class MoverItem(BaseModel):
    symbol: str
    name: Optional[str] = None
    price: Optional[float] = None
    change_percent: Optional[float] = None
    sentiment: int = 50
    ai_summary: str = ""


class MoversResponse(BaseModel):
    category: str
    items: List[MoverItem]
    source: str = "mock"


class SectorPerf(BaseModel):
    sector: str
    change_percent: float


class NewsArticle(BaseModel):
    title: str
    summary: Optional[str] = None
    ai_summary: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[str] = None
    sentiment: Optional[str] = None       # Positive / Neutral / Negative
    impact: Optional[str] = None          # High / Medium / Positive
    symbols: List[str] = []
    categories: List[str] = []


class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    source: str = "mock"


class AnalysisResponse(BaseModel):
    symbol: str
    name: Optional[str] = None
    quote: Optional[Quote] = None
    trend: str
    sentiment: SentimentScore
    risk_rating: Literal["Low", "Moderate", "High"]
    risk_level: int = Field(ge=1, le=5)
    explanation: str
    news: List[NewsArticle] = []
    candles: List[Candle] = []
    ai_powered: bool = False


class InsightCard(BaseModel):
    title: str
    direction: Literal["bull", "bear", "neu"]
    explanation: str
    confidence: int = Field(ge=0, le=100)
    related: List[str] = []


# ---------- AI assistant ----------
class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    ai_powered: bool = False
    related_symbols: List[str] = []


# ---------- Auth ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    plan: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Watchlist ----------
class WatchlistAdd(BaseModel):
    symbol: str
    name: Optional[str] = None


class WatchlistItemOut(BaseModel):
    id: int
    symbol: str
    name: Optional[str] = None
    created_at: str
