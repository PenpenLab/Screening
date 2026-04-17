"""
株価・財務データ取得サービス (同期版 / Streamlit用)
cachetools.TTLCache でキャッシュ (TTL 15分)
"""
from __future__ import annotations

from typing import Optional
import pandas as pd
import yfinance as yf
import streamlit as st
from cachetools import TTLCache

_info_cache: TTLCache = TTLCache(maxsize=500, ttl=900)
_hist_cache: TTLCache = TTLCache(maxsize=200, ttl=900)


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
    import time
    key = f"{market}:{symbol}"
    if key in _info_cache:
        return _info_cache[key]
    yf_symbol = _to_jp_symbol(symbol) if market == "JP" else symbol
    last_exc: Exception = RuntimeError("fetch failed")
    for attempt in range(4):
        try:
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            if not info or not isinstance(info, dict) or len(info) < 3:
                raise ValueError(f"yfinance から有効なデータを取得できませんでした: {yf_symbol}")
            _info_cache[key] = info
            return info
        except Exception as e:
            last_exc = e
            err_str = str(e)
            if "Too Many Requests" in err_str or "rate limit" in err_str.lower():
                time.sleep(2 ** attempt)  # 1s, 2s, 4s, 8s
                continue
            raise
    raise last_exc


@st.cache_data(ttl=900, show_spinner=False)
def fetch_history(symbol: str, market: str, period: str = "1y") -> pd.DataFrame:
    yf_symbol = _to_jp_symbol(symbol) if market == "JP" else symbol
    ticker = yf.Ticker(yf_symbol)
    return ticker.history(period=period)


@st.cache_data(ttl=900, show_spinner=False)
def search_stocks(query: str, market: str) -> list[dict]:
    try:
        results = yf.Search(query, max_results=15)
        filtered = []
        for q in results.quotes:
            sym = q.get("symbol", "")
            exchange = q.get("exchange", "")
            q_type = q.get("quoteType", "")
            if q_type not in ("EQUITY", "ETF"):
                continue
            if market == "JP":
                # .T サフィックスか日本の主要取引所コードを許容
                jp_exchanges = {"TKS", "OSA", "FKS", "NGO", "SAP", "JPX", "JPN", "TSE"}
                if not (sym.endswith(".T") or sym.endswith(".OS") or exchange in jp_exchanges):
                    continue
            elif market == "US":
                if "." in sym:
                    continue
            clean_sym = sym.replace(".T", "").replace(".OS", "") if market == "JP" else sym
            filtered.append({
                "symbol": clean_sym,
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
        "dividend_yield": _safe_float(info.get("dividendYield")),
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


# ── 財務諸表・株主データ ────────────────────────────────────────────────────

@st.cache_data(ttl=900, show_spinner=False)
def fetch_financials(symbol: str, market: str) -> dict:
    yf_symbol = _to_jp_symbol(symbol) if market == "JP" else symbol
    ticker = yf.Ticker(yf_symbol)
    out: dict = {}
    for key, attrs in [
        ("income", ["income_stmt", "financials"]),
        ("quarterly_income", ["quarterly_income_stmt", "quarterly_financials"]),
    ]:
        for attr in attrs:
            try:
                df = getattr(ticker, attr)
                if df is not None and not df.empty:
                    out[key] = df
                    break
            except Exception:
                continue
        if key not in out:
            out[key] = pd.DataFrame()
    return out


@st.cache_data(ttl=900, show_spinner=False)
def fetch_holders(symbol: str, market: str) -> pd.DataFrame:
    yf_symbol = _to_jp_symbol(symbol) if market == "JP" else symbol
    try:
        df = yf.Ticker(yf_symbol).institutional_holders
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# ── テクニカル指標計算 ─────────────────────────────────────────────────────

def calc_technical_indicators(hist: pd.DataFrame) -> dict:
    """RSI・MACD・移動平均と売買シグナルを算出して返す"""
    if hist is None or hist.empty:
        return {}
    close = hist["Close"]

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()

    # RSI (14期間, Wilderスムージング)
    delta = close.diff()
    avg_gain = delta.clip(lower=0).ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    avg_loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    # シグナル検出
    signals: list[tuple[str, str, str]] = []
    latest_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None

    if latest_rsi is not None:
        if latest_rsi < 30:
            signals.append(("買い", f"RSI {latest_rsi:.1f} — 売られすぎゾーン（30未満）", "bullish"))
        elif latest_rsi > 70:
            signals.append(("売り", f"RSI {latest_rsi:.1f} — 買われすぎゾーン（70超）", "bearish"))
        else:
            signals.append(("中立", f"RSI {latest_rsi:.1f} — 中立ゾーン（30〜70）", "neutral"))

    if len(macd_line) >= 2 and not pd.isna(macd_line.iloc[-1]):
        prev = float(macd_line.iloc[-2]) - float(signal_line.iloc[-2])
        curr = float(macd_line.iloc[-1]) - float(signal_line.iloc[-1])
        if prev < 0 <= curr:
            signals.append(("買い", "MACD がシグナル線を上抜け（ゴールデンクロス）", "bullish"))
        elif prev > 0 >= curr:
            signals.append(("売り", "MACD がシグナル線を下抜け（デッドクロス）", "bearish"))
        elif curr > 0:
            signals.append(("中立（強気）", "MACD > シグナル線（上昇モメンタム継続）", "bullish"))
        else:
            signals.append(("中立（弱気）", "MACD < シグナル線（下降モメンタム継続）", "bearish"))

    if not pd.isna(ma20.iloc[-1]) and not pd.isna(ma50.iloc[-1]) \
            and not pd.isna(ma20.iloc[-2]) and not pd.isna(ma50.iloc[-2]):
        prev = float(ma20.iloc[-2]) - float(ma50.iloc[-2])
        curr = float(ma20.iloc[-1]) - float(ma50.iloc[-1])
        if prev < 0 <= curr:
            signals.append(("買い", "MA20 が MA50 を上抜け（ゴールデンクロス）", "bullish"))
        elif prev > 0 >= curr:
            signals.append(("売り", "MA20 が MA50 を下抜け（デッドクロス）", "bearish"))
        elif curr > 0:
            signals.append(("中立（強気）", "MA20 > MA50（短期上昇トレンド）", "bullish"))
        else:
            signals.append(("中立（弱気）", "MA20 < MA50（短期下降トレンド）", "bearish"))

    latest_price = float(close.iloc[-1])
    latest_ma200 = float(ma200.iloc[-1]) if not pd.isna(ma200.iloc[-1]) else None
    if latest_ma200 is not None:
        pct_diff = (latest_price - latest_ma200) / latest_ma200 * 100
        label = "強気トレンド" if latest_price > latest_ma200 else "弱気トレンド"
        trend = "bullish" if latest_price > latest_ma200 else "bearish"
        signals.append((label, f"株価が MA200 の {pct_diff:+.1f}% {'上' if trend=='bullish' else '下'}（長期{'上昇' if trend=='bullish' else '下降'}トレンド）", trend))

    return {
        "close": close,
        "volume": hist["Volume"],
        "ma20": ma20, "ma50": ma50, "ma200": ma200,
        "rsi": rsi,
        "macd_line": macd_line, "signal_line": signal_line, "histogram": histogram,
        "signals": signals,
        "latest_rsi": latest_rsi,
    }
