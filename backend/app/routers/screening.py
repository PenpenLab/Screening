from fastapi import APIRouter, HTTPException, Query
from app.models.stock import ScreeningFilter, StockMetrics
from app.services.screening_service import screen_stocks

router = APIRouter(prefix="/api/screening", tags=["screening"])


@router.post("/japan", response_model=list[StockMetrics])
async def screen_japan(filters: ScreeningFilter):
    try:
        return await screen_stocks("JP", filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/us", response_model=list[StockMetrics])
async def screen_us(filters: ScreeningFilter):
    try:
        return await screen_stocks("US", filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
