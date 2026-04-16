"""
スクリーニングサービス (Streamlit用)
"""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional
import pandas as pd
import streamlit as st

from services.stock_service import fetch_info, build_metrics

# ── ユニバース ─────────────────────────────────────────────────────────────

JP_UNIVERSE = [
    "7203", "6758", "9984", "8035", "6861", "6098", "9433", "8306",
    "7974", "6501", "6752", "9432", "4519", "8316", "7267", "6367",
    "6902", "4661", "2914", "9022", "9021", "8411", "6702", "4543",
    "4568", "2802", "4307", "3382", "8001", "7751", "8031", "8002",
    "7011", "6954", "9101", "9104", "5401", "4004", "6503", "1925",
    "3407", "4452", "4901", "6971", "9020", "7733", "8058", "5108",
    "4063", "6645",
]

US_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "BRK-B",
    "UNH", "LLY", "JPM", "XOM", "V", "MA", "PG", "HD", "AVGO", "CVX",
    "MRK", "ABBV", "COST", "PEP", "ADBE", "KO", "WMT", "TMO", "MCD",
    "CSCO", "ACN", "NFLX", "ABT", "DHR", "NEE", "TXN", "PM", "LIN",
    "CRM", "ORCL", "AMD", "QCOM", "RTX", "AMGN", "HON", "IBM", "GE",
    "CAT", "UPS", "SBUX", "NOW", "INTC",
]


def _passes(m: dict, filters: dict) -> bool:
    def check_min(key: str, threshold: Optional[float]) -> bool:
        if threshold is None:
            return True
        v = m.get(key)
        return v is not None and v >= threshold

    def check_max(key: str, threshold: Optional[float]) -> bool:
        if threshold is None:
            return True
        v = m.get(key)
        return v is None or v <= threshold

    def check_range(key: str, lo: Optional[float], hi: Optional[float]) -> bool:
        v = m.get(key)
        if lo is not None and (v is None or v < lo):
            return False
        if hi is not None and (v is None or v > hi):
            return False
        return True

    checks = [
        check_range("per", filters.get("per_min"), filters.get("per_max")),
        check_range("pbr", filters.get("pbr_min"), filters.get("pbr_max")),
        check_min("roe", filters.get("roe_min")),
        check_min("roa", filters.get("roa_min")),
        check_min("operating_margin", filters.get("operating_margin_min")),
        check_min("revenue_growth", filters.get("revenue_growth_min")),
        check_min("earnings_growth", filters.get("earnings_growth_min")),
        check_min("dividend_yield", filters.get("dividend_yield_min")),
        check_min("equity_ratio", filters.get("equity_ratio_min")),
        check_max("debt_to_equity", filters.get("debt_to_equity_max")),
    ]
    if not all(checks):
        return False

    # 時価総額 (十億単位で比較)
    cap = m.get("market_cap")
    cap_min = filters.get("market_cap_min")
    cap_max = filters.get("market_cap_max")
    if cap is not None:
        cap_b = cap / 1e9
        if cap_min is not None and cap_b < cap_min:
            return False
        if cap_max is not None and cap_b > cap_max:
            return False
    elif cap_min is not None:
        return False

    return True


def screen_stocks(
    market: str,
    filters: dict,
    sort_by: str = "market_cap",
    sort_desc: bool = True,
    limit: int = 50,
    progress_bar=None,
) -> pd.DataFrame:
    universe = JP_UNIVERSE if market == "JP" else US_UNIVERSE
    results = []
    total = len(universe)

    for i, symbol in enumerate(universe):
        if progress_bar is not None:
            progress_bar.progress((i + 1) / total, text=f"{symbol} を取得中... ({i+1}/{total})")
        try:
            info = fetch_info(symbol, market)
            m = build_metrics(symbol, market, info)
            if _passes(m, filters):
                results.append(m)
        except Exception:
            continue

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)

    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=not sort_desc, na_position="last")

    return df.head(limit).reset_index(drop=True)
