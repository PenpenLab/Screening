import yfinance as yf
import pandas as pd
from typing import Optional
from cachetools import TTLCache
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.models.stock import StockMetrics, StockDetail, PriceHistory
from app.config import get_settings

settings = get_settings()
_cache: TTLCache = TTLCache(maxsize=500, ttl=settings.cache_ttl_seconds)
_executor = ThreadPoolExecutor(max_workers=10)


def _to_jp_symbol(symbol: str) -> str:
    """Convert 4-digit JP code to yfinance format."""
    if symbol.isdigit() and len(symbol) == 4:
        return f"{symbol}.T"
    return symbol


def _safe_float(val) -> Optional[float]:
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        return float(val)
    except Exception:
        return None


def _safe_int(val) -> Optional[int]:
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        return int(val)
    except Exception:
        return None


def _fetch_stock_info(symbol: str, market: str) -> dict:
    """Fetch raw info dict from yfinance (blocking)."""
    yf_symbol = _to_jp_symbol(symbol) if market == "JP" else symbol
    ticker = yf.Ticker(yf_symbol)
    return ticker.info


def _build_metrics(symbol: str, market: str, info: dict) -> StockMetrics:
    """Build StockMetrics from yfinance info dict."""
    currency = "JPY" if market == "JP" else (info.get("currency") or "USD")
    market_cap_raw = _safe_float(info.get("marketCap"))

    # P/S ratio
    price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
    trailing_ps = _safe_float(info.get("priceToSalesTrailing12Months"))

    # Equity ratio (JP: 自己資本比率) = equity / total_assets
    equity_ratio = None
    total_assets = _safe_float(info.get("totalAssets"))
    stockholders_equity = _safe_float(info.get("bookValue"))
    shares_outstanding = _safe_float(info.get("sharesOutstanding"))
    if stockholders_equity and shares_outstanding and total_assets and total_assets > 0:
        total_equity = stockholders_equity * shares_outstanding
        equity_ratio = (total_equity / total_assets) * 100

    return StockMetrics(
        symbol=symbol,
        name=info.get("longName") or info.get("shortName") or symbol,
        market=market,
        price=price,
        change_pct=_safe_float(info.get("regularMarketChangePercent")),
        market_cap=market_cap_raw,
        volume=_safe_int(info.get("regularMarketVolume")),
        per=_safe_float(info.get("trailingPE")),
        pbr=_safe_float(info.get("priceToBook")),
        psr=trailing_ps,
        ev_ebitda=_safe_float(info.get("enterpriseToEbitda")),
        roe=_safe_float(info.get("returnOnEquity")) * 100 if _safe_float(info.get("returnOnEquity")) else None,
        roa=_safe_float(info.get("returnOnAssets")) * 100 if _safe_float(info.get("returnOnAssets")) else None,
        operating_margin=_safe_float(info.get("operatingMargins")) * 100 if _safe_float(info.get("operatingMargins")) else None,
        net_margin=_safe_float(info.get("profitMargins")) * 100 if _safe_float(info.get("profitMargins")) else None,
        revenue_growth=_safe_float(info.get("revenueGrowth")) * 100 if _safe_float(info.get("revenueGrowth")) else None,
        earnings_growth=_safe_float(info.get("earningsGrowth")) * 100 if _safe_float(info.get("earningsGrowth")) else None,
        eps_growth=_safe_float(info.get("earningsQuarterlyGrowth")) * 100 if _safe_float(info.get("earningsQuarterlyGrowth")) else None,
        equity_ratio=equity_ratio,
        debt_to_equity=_safe_float(info.get("debtToEquity")),
        current_ratio=_safe_float(info.get("currentRatio")),
        dividend_yield=_safe_float(info.get("dividendYield")) * 100 if _safe_float(info.get("dividendYield")) else None,
        payout_ratio=_safe_float(info.get("payoutRatio")) * 100 if _safe_float(info.get("payoutRatio")) else None,
        fcf_yield=None,  # Calculated separately if needed
        peg_ratio=_safe_float(info.get("pegRatio")),
        bps=_safe_float(info.get("bookValue")),
        eps=_safe_float(info.get("trailingEps")),
        sector=info.get("sector"),
        industry=info.get("industry"),
        currency=currency,
    )


def _build_detail(symbol: str, market: str, info: dict) -> StockDetail:
    metrics = _build_metrics(symbol, market, info)
    data = metrics.model_dump()
    data.update(
        description=info.get("longBusinessSummary"),
        website=info.get("website"),
        employees=_safe_int(info.get("fullTimeEmployees")),
        country=info.get("country"),
        exchange=info.get("exchange"),
        week52_high=_safe_float(info.get("fiftyTwoWeekHigh")),
        week52_low=_safe_float(info.get("fiftyTwoWeekLow")),
        target_price=_safe_float(info.get("targetMeanPrice")),
        recommendation=info.get("recommendationKey"),
    )
    return StockDetail(**data)


async def get_stock_detail(symbol: str, market: str) -> StockDetail:
    cache_key = f"detail:{market}:{symbol}"
    if cache_key in _cache:
        return _cache[cache_key]

    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(_executor, _fetch_stock_info, symbol, market)
    result = _build_detail(symbol, market, info)
    _cache[cache_key] = result
    return result


async def get_stock_metrics(symbol: str, market: str) -> StockMetrics:
    cache_key = f"metrics:{market}:{symbol}"
    if cache_key in _cache:
        return _cache[cache_key]

    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(_executor, _fetch_stock_info, symbol, market)
    result = _build_metrics(symbol, market, info)
    _cache[cache_key] = result
    return result


def _fetch_history(symbol: str, market: str, period: str) -> list[PriceHistory]:
    yf_symbol = _to_jp_symbol(symbol) if market == "JP" else symbol
    ticker = yf.Ticker(yf_symbol)
    hist = ticker.history(period=period)
    records = []
    for date, row in hist.iterrows():
        records.append(PriceHistory(
            date=date.strftime("%Y-%m-%d"),
            open=round(float(row["Open"]), 2),
            high=round(float(row["High"]), 2),
            low=round(float(row["Low"]), 2),
            close=round(float(row["Close"]), 2),
            volume=int(row["Volume"]),
        ))
    return records


async def get_stock_history(symbol: str, market: str, period: str = "1y") -> list[PriceHistory]:
    cache_key = f"history:{market}:{symbol}:{period}"
    if cache_key in _cache:
        return _cache[cache_key]

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, _fetch_history, symbol, market, period)
    _cache[cache_key] = result
    return result


def _search_symbols(query: str, market: str) -> list[dict]:
    """Search symbols using yfinance search."""
    try:
        results = yf.Search(query, max_results=10)
        quotes = results.quotes
        filtered = []
        for q in quotes:
            symbol = q.get("symbol", "")
            exchange = q.get("exchange", "")
            q_type = q.get("quoteType", "")
            if q_type not in ("EQUITY", "ETF"):
                continue
            if market == "JP" and not (symbol.endswith(".T") or exchange in ("TKS", "OSA")):
                continue
            if market == "US" and ("." in symbol):
                continue
            filtered.append({
                "symbol": symbol.replace(".T", "") if market == "JP" else symbol,
                "name": q.get("longname") or q.get("shortname", symbol),
                "exchange": exchange,
                "type": q_type,
            })
        return filtered[:8]
    except Exception:
        return []


async def search_stocks(query: str, market: str) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _search_symbols, query, market)
