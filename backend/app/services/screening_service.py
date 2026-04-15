"""
Stock screening service.
Uses predefined universe lists + yfinance for metric fetching.
"""
import asyncio
from typing import Optional
from app.models.stock import StockMetrics, ScreeningFilter
from app.services.stock_service import get_stock_metrics

# -----------------------------------------------------------------------
# Default stock universes (expandable)
# -----------------------------------------------------------------------

JP_UNIVERSE = [
    # Nikkei 225 core + major stocks (証券コード)
    "7203", "6758", "9984", "8035", "6861", "6098", "9433", "8306",
    "7974", "6501", "6752", "9432", "4519", "8316", "7267", "6367",
    "6902", "4661", "2914", "9022", "9021", "8411", "6702", "4543",
    "4568", "2802", "4307", "3382", "8001", "7751", "8031", "8002",
    "7011", "6954", "9101", "9104", "5401", "4004", "6503", "1925",
    "3407", "4452", "4901", "6971", "9020", "7733", "8058", "5108",
    "4063", "6645",
]

US_UNIVERSE = [
    # S&P 500 core
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "BRK-B",
    "UNH", "LLY", "JPM", "XOM", "V", "MA", "PG", "HD", "AVGO", "CVX",
    "MRK", "ABBV", "COST", "PEP", "ADBE", "KO", "WMT", "TMO", "MCD",
    "CSCO", "ACN", "NFLX", "ABT", "DHR", "NEE", "TXN", "PM", "LIN",
    "CRM", "ORCL", "AMD", "QCOM", "RTX", "AMGN", "HON", "IBM", "GE",
    "CAT", "UPS", "SBUX", "NOW", "INTC",
]


def _apply_filter(m: StockMetrics, f: ScreeningFilter) -> bool:
    """Return True if the stock passes all filter conditions."""
    checks = [
        (f.per_min, f.per_max, m.per),
        (f.pbr_min, f.pbr_max, m.pbr),
    ]
    for lo, hi, val in checks:
        if lo is not None and (val is None or val < lo):
            return False
        if hi is not None and (val is None or val > hi):
            return False

    single_min = [
        (f.roe_min, m.roe),
        (f.roa_min, m.roa),
        (f.operating_margin_min, m.operating_margin),
        (f.revenue_growth_min, m.revenue_growth),
        (f.earnings_growth_min, m.earnings_growth),
        (f.dividend_yield_min, m.dividend_yield),
        (f.equity_ratio_min, m.equity_ratio),
    ]
    for threshold, val in single_min:
        if threshold is not None and (val is None or val < threshold):
            return False

    single_max = [
        (f.debt_to_equity_max, m.debt_to_equity),
    ]
    for threshold, val in single_max:
        if threshold is not None and val is not None and val > threshold:
            return False

    # Market cap filter (stored in raw units, filter in billions)
    if f.market_cap_min is not None or f.market_cap_max is not None:
        cap = m.market_cap
        if cap is None:
            return False
        cap_b = cap / 1e9
        if f.market_cap_min is not None and cap_b < f.market_cap_min:
            return False
        if f.market_cap_max is not None and cap_b > f.market_cap_max:
            return False

    # Sector filter
    if f.sectors and m.sector and m.sector not in f.sectors:
        return False

    return True


def _sort_key(m: StockMetrics, sort_by: str) -> float:
    val = getattr(m, sort_by, None)
    if val is None:
        return float("-inf")
    return float(val)


async def _fetch_with_fallback(symbol: str, market: str) -> Optional[StockMetrics]:
    try:
        return await get_stock_metrics(symbol, market)
    except Exception:
        return None


async def screen_stocks(market: str, filters: ScreeningFilter) -> list[StockMetrics]:
    universe = JP_UNIVERSE if market == "JP" else US_UNIVERSE
    tasks = [_fetch_with_fallback(sym, market) for sym in universe]
    results = await asyncio.gather(*tasks)

    passed = []
    for m in results:
        if m is None:
            continue
        if _apply_filter(m, filters):
            passed.append(m)

    reverse = filters.sort_order == "desc"
    passed.sort(key=lambda m: _sort_key(m, filters.sort_by), reverse=reverse)
    return passed[: filters.limit]
