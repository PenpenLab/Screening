"""
株価・財務データ取得サービス (同期版 / Streamlit用)
cachetools.TTLCache でキャッシュ (TTL 15分)
"""
from __future__ import annotations

from typing import Optional
import pandas as pd
import requests
import yfinance as yf
import streamlit as st
from cachetools import TTLCache

_info_cache: TTLCache = TTLCache(maxsize=500, ttl=900)
_hist_cache: TTLCache = TTLCache(maxsize=200, ttl=900)

# Custom requests session with browser-like headers to reduce Yahoo Finance rate limiting
_session = requests.Session()
_session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
})


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

def fetch_info(symbol: str, market: str) -> dict:
    key = f"{market}:{symbol}"
    if key in _info_cache:
        return _info_cache[key]
    yf_symbol = _to_jp_symbol(symbol) if market == "JP" else symbol
    ticker = yf.Ticker(yf_symbol, session=_session)
    info = ticker.info
    # 空dictや不正なレスポンスを弾く
    if not info or not isinstance(info, dict) or len(info) < 3:
        raise ValueError(f"yfinance から有効なデータを取得できませんでした: {yf_symbol}")
    _info_cache[key] = info
    return info


@st.cache_data(ttl=900, show_spinner=False)
def fetch_history(symbol: str, market: str, period: str = "1y") -> pd.DataFrame:
    yf_symbol = _to_jp_symbol(symbol) if market == "JP" else symbol
    ticker = yf.Ticker(yf_symbol, session=_session)
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


# ── 日本語会社名マッピング ─────────────────────────────────────────────────

JP_NAME_MAP: dict[str, str] = {
    "7203": "トヨタ自動車",
    "6758": "ソニーグループ",
    "9984": "ソフトバンクグループ",
    "8035": "東京エレクトロン",
    "6861": "キーエンス",
    "6098": "リクルートホールディングス",
    "9433": "KDDI",
    "8306": "三菱UFJフィナンシャル・グループ",
    "7974": "任天堂",
    "6501": "日立製作所",
    "6752": "パナソニックホールディングス",
    "9432": "日本電信電話（NTT）",
    "4519": "中外製薬",
    "8316": "三井住友フィナンシャルグループ",
    "7267": "本田技研工業",
    "6367": "ダイキン工業",
    "6902": "デンソー",
    "4661": "オリエンタルランド",
    "2914": "日本たばこ産業（JT）",
    "9022": "東海旅客鉄道（JR東海）",
    "9021": "西日本旅客鉄道（JR西日本）",
    "8411": "みずほフィナンシャルグループ",
    "6702": "富士通",
    "4543": "テルモ",
    "4568": "第一三共",
    "2802": "味の素",
    "4307": "野村総合研究所",
    "3382": "セブン&アイ・ホールディングス",
    "8001": "伊藤忠商事",
    "7751": "キヤノン",
    "8031": "三井物産",
    "8002": "丸紅",
    "7011": "三菱重工業",
    "6954": "ファナック",
    "9101": "日本郵船",
    "9104": "商船三井",
    "5401": "日本製鉄",
    "4004": "レゾナック・ホールディングス",
    "6503": "三菱電機",
    "1925": "大和ハウス工業",
    "3407": "旭化成",
    "4452": "花王",
    "4901": "富士フイルムホールディングス",
    "6971": "京セラ",
    "9020": "東日本旅客鉄道（JR東日本）",
    "7733": "オリンパス",
    "8058": "三菱商事",
    "5108": "ブリヂストン",
    "4063": "信越化学工業",
    "6645": "オムロン",
}

US_NAME_MAP: dict[str, str] = {
    "AAPL": "アップル",
    "MSFT": "マイクロソフト",
    "NVDA": "エヌビディア",
    "AMZN": "アマゾン・ドット・コム",
    "META": "メタ・プラットフォームズ",
    "GOOGL": "アルファベット",
    "TSLA": "テスラ",
    "BRK-B": "バークシャー・ハサウェイ",
    "UNH": "ユナイテッドヘルス・グループ",
    "LLY": "イーライリリー",
    "JPM": "JPモルガン・チェース",
    "XOM": "エクソンモービル",
    "V": "ビザ",
    "MA": "マスターカード",
    "PG": "プロクター・アンド・ギャンブル",
    "HD": "ホーム・デポ",
    "AVGO": "ブロードコム",
    "CVX": "シェブロン",
    "MRK": "メルク",
    "ABBV": "アッヴィ",
    "COST": "コストコ・ホールセール",
    "PEP": "ペプシコ",
    "ADBE": "アドビ",
    "KO": "コカ・コーラ",
    "WMT": "ウォルマート",
    "TMO": "サーモフィッシャーサイエンティフィック",
    "MCD": "マクドナルド",
    "CSCO": "シスコシステムズ",
    "ACN": "アクセンチュア",
    "NFLX": "ネットフリックス",
    "ABT": "アボット・ラボラトリーズ",
    "DHR": "ダナハー",
    "NEE": "ネクストエラ・エナジー",
    "TXN": "テキサス・インスツルメンツ",
    "PM": "フィリップ・モリス・インターナショナル",
    "LIN": "リンデ",
    "CRM": "セールスフォース",
    "ORCL": "オラクル",
    "AMD": "アドバンスト・マイクロ・デバイセズ（AMD）",
    "QCOM": "クアルコム",
    "RTX": "RTXコーポレーション",
    "AMGN": "アムジェン",
    "HON": "ハネウェル・インターナショナル",
    "IBM": "IBM",
    "GE": "GEエアロスペース",
    "CAT": "キャタピラー",
    "UPS": "ユナイテッド・パーセル・サービス（UPS）",
    "SBUX": "スターバックス",
    "NOW": "サービスナウ",
    "INTC": "インテル",
}


# ── info dict → 指標 dict ──────────────────────────────────────────────────

def build_metrics(symbol: str, market: str, info: dict) -> dict:
    currency = "JPY" if market == "JP" else (info.get("currency") or "USD")

    equity_ratio = None
    total_assets = _safe_float(info.get("totalAssets"))
    book_value = _safe_float(info.get("bookValue"))
    shares = _safe_float(info.get("sharesOutstanding"))
    if book_value and shares and total_assets and total_assets > 0:
        equity_ratio = (book_value * shares / total_assets) * 100

    def pct(key: str) -> Optional[float]:
        v = _safe_float(info.get(key))
        return v * 100 if v is not None else None

    name_map = JP_NAME_MAP if market == "JP" else US_NAME_MAP
    name = name_map.get(symbol) or info.get("longName") or info.get("shortName") or symbol

    return {
        "symbol": symbol,
        "name": name,
        "market": market,
        "currency": currency,
        "price": _safe_float(info.get("currentPrice") or info.get("regularMarketPrice")),
        "change_pct": _safe_float(info.get("regularMarketChangePercent")),
        "market_cap": _safe_float(info.get("marketCap")),
        "volume": _safe_int(info.get("regularMarketVolume")),
        "per": _safe_float(info.get("trailingPE")),
        "pbr": _safe_float(info.get("priceToBook")),
        "psr": _safe_float(info.get("priceToSalesTrailing12Months")),
        "ev_ebitda": _safe_float(info.get("enterpriseToEbitda")),
        "peg_ratio": _safe_float(info.get("pegRatio")),
        "roe": pct("returnOnEquity"),
        "roa": pct("returnOnAssets"),
        "operating_margin": pct("operatingMargins"),
        "net_margin": pct("profitMargins"),
        "revenue_growth": pct("revenueGrowth"),
        "earnings_growth": pct("earningsGrowth"),
        "eps_growth": pct("earningsQuarterlyGrowth"),
        "equity_ratio": equity_ratio,
        "debt_to_equity": _safe_float(info.get("debtToEquity")),
        "current_ratio": _safe_float(info.get("currentRatio")),
        "dividend_yield": pct("dividendYield"),
        "payout_ratio": pct("payoutRatio"),
        "eps": _safe_float(info.get("trailingEps")),
        "bps": _safe_float(info.get("bookValue")),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
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
