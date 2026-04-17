"""
スクリーニングサービス (Streamlit用)
"""
from __future__ import annotations

import time
from typing import Optional
import pandas as pd
import streamlit as st

from stock_service import fetch_info, build_metrics, _info_cache

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
    # メガキャップ・テック
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA",
    # 金融
    "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS",
    # ヘルスケア
    "UNH", "LLY", "MRK", "ABBV", "JNJ", "ABT", "TMO", "DHR", "PFE", "AMGN",
    # 生活必需品・消費
    "PG", "KO", "PEP", "WMT", "COST", "MCD", "SBUX", "NKE",
    # エネルギー
    "XOM", "CVX",
    # 素材・産業
    "LIN", "CAT", "HON", "GE", "RTX", "UPS",
    # テクノロジー（セミコン・ソフト）
    "AVGO", "ADBE", "CRM", "ORCL", "AMD", "QCOM", "TXN", "CSCO", "IBM", "INTC", "NOW",
    # 通信・メディア
    "NFLX", "ACN",
    # ヘルスケア・公益
    "NEE", "PM", "HD",
    # 成長株・新興テック
    "PLTR", "SNOW", "CRWD", "NET", "DDOG", "MDB", "ZS", "PANW",
    "UBER", "ABNB", "COIN", "HOOD", "RBLX", "SPOT",
    "ARM", "SMCI", "MSTR",
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
        check_min("eps_growth", filters.get("eps_growth_min")),
        check_min("dividend_yield", filters.get("dividend_yield_min")),
        check_min("equity_ratio", filters.get("equity_ratio_min")),
        check_max("debt_to_equity", filters.get("debt_to_equity_max")),
    ]
    if not all(checks):
        return False

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
) -> tuple[pd.DataFrame, list[str]]:
    """
    Returns (DataFrame, error_list).
    error_list is non-empty when some symbols failed to fetch.
    """
    universe = JP_UNIVERSE if market == "JP" else US_UNIVERSE
    results = []
    errors: list[str] = []
    total = len(universe)

    for i, symbol in enumerate(universe):
        if progress_bar is not None:
            progress_bar.progress((i + 1) / total, text=f"{symbol} を取得中... ({i+1}/{total})")
        cache_key = f"{market}:{symbol}"
        is_cached = cache_key in _info_cache
        for attempt in range(3):
            try:
                info = fetch_info(symbol, market)
                m = build_metrics(symbol, market, info)
                if _passes(m, filters):
                    results.append(m)
                break
            except Exception as e:
                err_str = str(e)
                is_rate_limit = "Too Many Requests" in err_str or "rate limit" in err_str.lower()
                if is_rate_limit and attempt < 2:
                    time.sleep(3 * (2 ** attempt))  # 3s, 6s
                    continue
                errors.append(f"{symbol}: {e}")
                break
        # キャッシュミス（実際にネットワーク通信した）場合のみ待機
        if not is_cached:
            time.sleep(0.2)

    if not results:
        return pd.DataFrame(), errors

    df = pd.DataFrame(results)
    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=not sort_desc, na_position="last")

    return df.head(limit).reset_index(drop=True), errors
