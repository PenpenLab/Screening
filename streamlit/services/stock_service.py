"""
株価・財務データ取得サービス (同期版 / Streamlit用)
@st.cache_data でキャッシュ (TTL 15分)
"""
from __future__ import annotations

from typing import Optional
import pandas as pd
import yfinance as yf
import streamlit as st


# ── ヘルパー ──────────────────────────────────────────────────────────────

def _to_jp_symbol(symbol: str) -> str:
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


# ── データ取得 ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=900, show_spinner=False)
def fetch_info(symbol: str, market: str) -> dict:
    yf_symbol = _to_jp_symbol(symbol) if market == "JP" else symbol
    ticker = yf.Ticker(yf_symbol)
    return ticker.info


@st.cache_data(ttl=900, show_spinner=False)
def fetch_history(symbol: str, market: str, period: str = "1y") -> pd.DataFrame:
    yf_symbol = _to_jp_symbol(symbol) if market == "JP" else symbol
    ticker = yf.Ticker(yf_symbol)
    return ticker.history(period=period)


@st.cache_data(ttl=900, show_spinner=False)
def search_stocks(query: str, market: str) -> list[dict]:
    try:
        results = yf.Search(query, max_results=10)
        filtered = []
        for q in results.quotes:
            sym = q.get("symbol", "")
            exchange = q.get("exchange", "")
            q_type = q.get("quoteType", "")
            if q_type not in ("EQUITY", "ETF"):
                continue
            if market == "JP" and not (sym.endswith(".T") or exchange in ("TKS", "OSA")):
                continue
            if market == "US" and "." in sym:
                continue
            filtered.append({
                "symbol": sym.replace(".T", "") if market == "JP" else sym,
                "name": q.get("longname") or q.get("shortname", sym),
                "exchange": exchange,
            })
        return filtered[:8]
    except Exception:
        return []


# ── info dict → 指標 dict ──────────────────────────────────────────────────

def build_metrics(symbol: str, market: str, info: dict) -> dict:
    currency = "JPY" if market == "JP" else (info.get("currency") or "USD")

    # 自己資本比率
    equity_ratio = None
    total_assets = _safe_float(info.get("totalAssets"))
    book_value = _safe_float(info.get("bookValue"))
    shares = _safe_float(info.get("sharesOutstanding"))
    if book_value and shares and total_assets and total_assets > 0:
        equity_ratio = (book_value * shares / total_assets) * 100

    def pct(key: str) -> Optional[float]:
        v = _safe_float(info.get(key))
        return v * 100 if v is not None else None

    return {
        "symbol": symbol,
        "name": info.get("longName") or info.get("shortName") or symbol,
        "market": market,
        "currency": currency,
        "price": _safe_float(info.get("currentPrice") or info.get("regularMarketPrice")),
        "change_pct": _safe_float(info.get("regularMarketChangePercent")),
        "market_cap": _safe_float(info.get("marketCap")),
        "volume": _safe_int(info.get("regularMarketVolume")),
        # Valuation
        "per": _safe_float(info.get("trailingPE")),
        "pbr": _safe_float(info.get("priceToBook")),
        "psr": _safe_float(info.get("priceToSalesTrailing12Months")),
        "ev_ebitda": _safe_float(info.get("enterpriseToEbitda")),
        "peg_ratio": _safe_float(info.get("pegRatio")),
        # Profitability
        "roe": pct("returnOnEquity"),
        "roa": pct("returnOnAssets"),
        "operating_margin": pct("operatingMargins"),
        "net_margin": pct("profitMargins"),
        # Growth
        "revenue_growth": pct("revenueGrowth"),
        "earnings_growth": pct("earningsGrowth"),
        "eps_growth": pct("earningsQuarterlyGrowth"),
        # Health
        "equity_ratio": equity_ratio,
        "debt_to_equity": _safe_float(info.get("debtToEquity")),
        "current_ratio": _safe_float(info.get("currentRatio")),
        # Returns
        "dividend_yield": pct("dividendYield"),
        "payout_ratio": pct("payoutRatio"),
        # Misc
        "eps": _safe_float(info.get("trailingEps")),
        "bps": _safe_float(info.get("bookValue")),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        # Detail
        "description": info.get("longBusinessSummary"),
        "website": info.get("website"),
        "employees": _safe_int(info.get("fullTimeEmployees")),
        "country": info.get("country"),
        "exchange": info.get("exchange"),
        "week52_high": _safe_float(info.get("fiftyTwoWeekHigh")),
        "week52_low": _safe_float(info.get("fiftyTwoWeekLow")),
        "target_price": _safe_float(info.get("targetMeanPrice")),
        "recommendation": info.get("recommendationKey"),
    }


def get_stock_metrics(symbol: str, market: str) -> dict:
    info = fetch_info(symbol, market)
    return build_metrics(symbol, market, info)
