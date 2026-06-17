"""AI intelligence endpoints: analyzer, insights, assistant chat."""
from fastapi import APIRouter

from ..schemas import (
    AnalysisResponse, InsightCard, ChatRequest, ChatResponse,
)
from ..services import market, ai

router = APIRouter(prefix="/api/ai", tags=["AI Intelligence"])


@router.get("/analyze/{symbol}", response_model=AnalysisResponse)
async def analyze(symbol: str):
    """Full AI analysis of a stock in plain language."""
    return await market.analyze(symbol)


@router.get("/insights", response_model=list[InsightCard])
async def insights():
    """Dynamic AI market insight cards."""
    return await market.get_insights()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Conversational AI assistant — 'Ask Nexora Anything'."""
    history = [{"role": m.role, "content": m.content} for m in req.history]
    reply, ai_powered = await ai.chat_reply(req.message, history)
    return ChatResponse(reply=reply, ai_powered=ai_powered)
