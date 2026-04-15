from pydantic import BaseModel
from typing import Optional


class StockBasic(BaseModel):
    symbol: str
    name: str
    market: str  # "JP" | "US"
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    currency: str = "USD"


class StockMetrics(BaseModel):
    symbol: str
    name: str
    market: str
    price: Optional[float] = None
    change_pct: Optional[float] = None
    market_cap: Optional[float] = None
    volume: Optional[int] = None
    # Valuation
    per: Optional[float] = None          # P/E Ratio
    pbr: Optional[float] = None          # P/B Ratio
    psr: Optional[float] = None          # P/S Ratio
    ev_ebitda: Optional[float] = None
    # Profitability
    roe: Optional[float] = None
    roa: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    # Growth
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    eps_growth: Optional[float] = None
    # Financial Health
    equity_ratio: Optional[float] = None       # 自己資本比率 (JP)
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    # Shareholder Returns
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    # Extra US metrics
    fcf_yield: Optional[float] = None
    peg_ratio: Optional[float] = None
    # Extra JP metrics
    bps: Optional[float] = None           # 1株純資産
    eps: Optional[float] = None
    # Sector info
    sector: Optional[str] = None
    industry: Optional[str] = None
    currency: str = "USD"


class StockDetail(StockMetrics):
    description: Optional[str] = None
    website: Optional[str] = None
    employees: Optional[int] = None
    country: Optional[str] = None
    exchange: Optional[str] = None
    # 52-week range
    week52_high: Optional[float] = None
    week52_low: Optional[float] = None
    # Analyst
    target_price: Optional[float] = None
    recommendation: Optional[str] = None


class PriceHistory(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class ScreeningFilter(BaseModel):
    # Valuation
    per_min: Optional[float] = None
    per_max: Optional[float] = None
    pbr_min: Optional[float] = None
    pbr_max: Optional[float] = None
    # Profitability
    roe_min: Optional[float] = None
    roa_min: Optional[float] = None
    operating_margin_min: Optional[float] = None
    # Growth
    revenue_growth_min: Optional[float] = None
    earnings_growth_min: Optional[float] = None
    # Shareholder Returns
    dividend_yield_min: Optional[float] = None
    # Financial Health
    equity_ratio_min: Optional[float] = None  # JP
    debt_to_equity_max: Optional[float] = None
    # Market Cap (in billions)
    market_cap_min: Optional[float] = None
    market_cap_max: Optional[float] = None
    # Sector filter
    sectors: Optional[list[str]] = None
    # Sort
    sort_by: str = "market_cap"
    sort_order: str = "desc"
    limit: int = 50


class AIAnalysisRequest(BaseModel):
    symbol: str
    market: str  # "JP" | "US"
    language: str = "ja"  # "ja" | "en"


class AIAnalysisResponse(BaseModel):
    symbol: str
    summary: str
    strengths: list[str]
    risks: list[str]
    verdict: str  # "bullish" | "neutral" | "bearish"
    verdict_reason: str
    disclaimer: str
