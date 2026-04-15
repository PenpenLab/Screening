from fastapi import APIRouter, HTTPException, Query
from app.models.stock import StockDetail, PriceHistory
from app.services.stock_service import get_stock_detail, get_stock_history, search_stocks

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    market: str = Query("US", pattern="^(JP|US)$"),
):
    results = await search_stocks(q, market)
    return {"results": results}


@router.get("/{symbol}", response_model=StockDetail)
async def get_stock(
    symbol: str,
    market: str = Query("US", pattern="^(JP|US)$"),
):
    try:
        return await get_stock_detail(symbol.upper(), market)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock not found: {e}")


@router.get("/{symbol}/history", response_model=list[PriceHistory])
async def get_history(
    symbol: str,
    market: str = Query("US", pattern="^(JP|US)$"),
    period: str = Query("1y", pattern="^(1mo|3mo|6mo|1y|2y|5y)$"),
):
    try:
        return await get_stock_history(symbol.upper(), market, period)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"History not found: {e}")
