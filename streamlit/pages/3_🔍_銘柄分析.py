"""
銘柄分析ページ — ティッカー直接入力 → 4タブ分析
"""
import json
import streamlit as st

from stock_service import (
    fetch_info, fetch_history, fetch_financials, fetch_holders,
    build_metrics, calc_technical_indicators, search_stocks,
)
from ui_components import (
    fmt_price, fmt_cap, delta_color,
    render_fundamental_tab, render_technical_tab, render_market_tab,
    _render_ai_result,
)
from ai_service import analyze_stock_full

st.set_page_config(page_title="銘柄分析", page_icon="🔍", layout="wide")
st.title("🔍 銘柄分析")
st.caption("銘柄コード・ティッカーで検索 → 業績・テクニカル・需給・AI総合分析")

# ── サイドバー: 検索フォーム ──────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 銘柄検索")
    market = st.radio("市場", ["JP", "US"], horizontal=True, key="anal_market_radio")
    label = "銘柄コード" if market == "JP" else "ティッカー"
    placeholder = "例: 7203 / 9984" if market == "JP" else "例: AAPL / NVDA"
    query = st.text_input(
        label,
        placeholder=placeholder,
        key="anal_query",
    )

    symbol: str | None = None

    if query:
        q = query.strip()

        # JP市場で4桁数字なら直接コードとして扱う
        if market == "JP" and q.isdigit() and len(q) == 4:
            symbol = q
            st.success(f"証券コード: **{symbol}**")
        else:
            results = search_stocks(q, market)
            if results:
                options = {f"{r['name']}  ({r['symbol']})": r["symbol"] for r in results}
                chosen = st.selectbox("銘柄を選択", list(options.keys()), key="anal_select")
                symbol = options[chosen]
            else:
                st.warning("検索結果が見つかりませんでした。\n\n日本株は4桁コード (例: 9984)、米国株はティッカー (例: AAPL) で入力してください。")

    if symbol:
        st.markdown(f"選択中: **{symbol}** ({market})")
        if st.button("🔍 分析開始", type="primary", use_container_width=True):
            st.session_state["anal_symbol"] = symbol
            st.session_state["anal_market_val"] = market
            # データをクリアして再取得
            for k in ["anal_m", "anal_info", "anal_hist", "anal_fin", "anal_holders", "anal_ai_result"]:
                st.session_state.pop(k, None)

# ── 分析表示 ──────────────────────────────────────────────────────────────
if "anal_symbol" not in st.session_state:
    st.info("👈 左のサイドバーで市場を選択し、銘柄名またはティッカーを入力して「分析開始」を押してください。")
    st.stop()

sym = st.session_state["anal_symbol"]
mkt = st.session_state["anal_market_val"]

# データ取得（セッションキャッシュ）
if "anal_m" not in st.session_state:
    with st.spinner(f"{sym} のデータを取得中..."):
        try:
            info = fetch_info(sym, mkt)
            st.session_state["anal_m"] = build_metrics(sym, mkt, info)
            st.session_state["anal_info"] = info
            st.session_state["anal_hist"] = fetch_history(sym, mkt, "1y")
            st.session_state["anal_fin"] = fetch_financials(sym, mkt)
            st.session_state["anal_holders"] = fetch_holders(sym, mkt)
        except Exception as e:
            st.error(f"データ取得に失敗しました: {e}")
            st.stop()

m = st.session_state["anal_m"]
info = st.session_state["anal_info"]
hist = st.session_state["anal_hist"]
fin_data = st.session_state["anal_fin"]
holders = st.session_state["anal_holders"]
indicators = calc_technical_indicators(hist)

currency = m["currency"]

# ── ヘッダー ──────────────────────────────────────────────────────────────
st.subheader(f"{m['name']}  `{sym}`  —  {m.get('sector') or ''}")
h1, h2, h3, h4, h5 = st.columns(5)
h1.metric("株価", fmt_price(m["price"], currency),
          f"{m['change_pct']:+.2f}%" if m["change_pct"] is not None else None,
          delta_color=delta_color(m["change_pct"]))
h2.metric("時価総額", fmt_cap(m["market_cap"], currency))
h3.metric("52週 高値", fmt_price(m["week52_high"], currency))
h4.metric("52週 安値", fmt_price(m["week52_low"], currency))
h5.metric("推奨", m.get("recommendation") or "—")

st.markdown("---")

# ── 4タブ ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 業績トレンド",
    "📈 テクニカル / 売買シグナル",
    "🏛 需給・マクロ",
    "🤖 Claude AI 総合分析",
])

with tab1:
    render_fundamental_tab(m, fin_data)

with tab2:
    render_technical_tab(indicators, m)

with tab3:
    render_market_tab(m, info, holders)

with tab4:
    has_key = bool(st.secrets.get("ANTHROPIC_API_KEY", ""))
    if not has_key:
        st.info("AI分析を使用するには Streamlit Cloud の Secrets に `ANTHROPIC_API_KEY` を設定してください。")
    else:
        signals = indicators.get("signals", [])
        tech_summary = "\n".join(
            f"{'買い' if s[2]=='bullish' else '売り' if s[2]=='bearish' else '中立'}: {s[1]}"
            for s in signals
        ) if signals else "テクニカルデータなし"

        if st.button("🤖 AI 総合分析を実行", type="primary", key="ai_full"):
            with st.spinner("Claude が分析中..."):
                try:
                    result = analyze_stock_full(sym, mkt, json.dumps(m), tech_summary)
                    st.session_state["anal_ai_result"] = result
                except Exception as e:
                    st.error(f"AI分析に失敗しました: {e}")

        if "anal_ai_result" in st.session_state:
            _render_ai_result(st.session_state["anal_ai_result"])
