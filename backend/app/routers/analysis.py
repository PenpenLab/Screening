from fastapi import APIRouter, HTTPException
from app.models.stock import AIAnalysisRequest, AIAnalysisResponse
from app.services.stock_service import get_stock_detail
from app.services.ai_service import analyze_stock
from app.config import get_settings

router = APIRouter(prefix="/api/analysis", tags=["analysis"])
settings = get_settings()


@router.post("/ai", response_model=AIAnalysisResponse)
async def ai_analysis(request: AIAnalysisRequest):
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="AI analysis not available: ANTHROPIC_API_KEY not configured",
        )
    try:
        detail = await get_stock_detail(request.symbol.upper(), request.market)
        return await analyze_stock(request, detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
