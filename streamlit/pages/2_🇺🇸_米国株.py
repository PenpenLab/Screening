"""
米国株スクリーニングページ
"""
import streamlit as st
import pandas as pd

from services.screening_service import screen_stocks
from services.ui_components import render_screening_table, render_stock_detail

st.set_page_config(page_title="米国株スクリーニング", page_icon="🇺🇸", layout="wide")

st.title("🇺🇸 米国株スクリーニング")
st.caption("NYSE/NASDAQ上場銘柄 · 米国株に最適な指標でフィルタリング")

# ── サイドバー: フィルター ────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 スクリーニング条件")

    st.subheader("バリュエーション")
    per_col1, per_col2 = st.columns(2)
    per_min = per_col1.number_input("P/E 下限", min_value=0.0, value=0.0, step=1.0, format="%.1f")
    per_max = per_col2.number_input("P/E 上限", min_value=0.0, value=0.0, step=1.0, format="%.1f",
                                     help="0 = 上限なし")
    pbr_col1, pbr_col2 = st.columns(2)
    pbr_min = pbr_col1.number_input("P/B 下限", min_value=0.0, value=0.0, step=0.1, format="%.2f")
    pbr_max = pbr_col2.number_input("P/B 上限", min_value=0.0, value=0.0, step=0.1, format="%.2f",
                                     help="0 = 上限なし")

    st.subheader("収益性")
    roe_min = st.number_input("ROE 最低 (%)", min_value=0.0, value=0.0, step=1.0)
    op_margin_min = st.number_input("営業利益率 最低 (%)", min_value=0.0, value=0.0, step=1.0)

    st.subheader("財務健全性")
    de_max = st.number_input("D/E Ratio 最大", min_value=0.0, value=0.0, step=0.5, format="%.1f",
                              help="負債対資本比率。0 = 上限なし")

    st.subheader("成長性")
    rev_growth_min = st.number_input("売上高成長率 最低 (%)", value=0.0, step=1.0)
    eps_growth_min = st.number_input("EPS 成長率 最低 (%)", value=0.0, step=1.0)

    st.subheader("株主還元")
    div_yield_min = st.number_input("配当利回り 最低 (%)", min_value=0.0, value=0.0, step=0.5)

    st.subheader("時価総額")
    cap_col1, cap_col2 = st.columns(2)
    cap_min = cap_col1.number_input("下限 ($B)", min_value=0.0, value=0.0, step=10.0)
    cap_max = cap_col2.number_input("上限 ($B)", min_value=0.0, value=0.0, step=10.0,
                                     help="0 = 上限なし")

    st.subheader("並び替え")
    sort_options = {
        "Market Cap": "market_cap", "P/E": "per", "P/B": "pbr",
        "ROE": "roe", "Dividend Yield": "dividend_yield",
        "Revenue Growth": "revenue_growth", "EPS Growth": "eps_growth",
        "Operating Margin": "operating_margin",
    }
    sort_label = st.selectbox("並び替え基準", list(sort_options.keys()))
    sort_desc = st.checkbox("降順", value=True)

    run_btn = st.button("🚀 スクリーニング実行", type="primary", use_container_width=True)

# ── メイン ────────────────────────────────────────────────────────────────
if run_btn:
    filters: dict = {}
    if per_min > 0: filters["per_min"] = per_min
    if per_max > 0: filters["per_max"] = per_max
    if pbr_min > 0: filters["pbr_min"] = pbr_min
    if pbr_max > 0: filters["pbr_max"] = pbr_max
    if roe_min > 0: filters["roe_min"] = roe_min
    if op_margin_min > 0: filters["operating_margin_min"] = op_margin_min
    if de_max > 0: filters["debt_to_equity_max"] = de_max
    if rev_growth_min != 0: filters["revenue_growth_min"] = rev_growth_min
    if eps_growth_min != 0: filters["earnings_growth_min"] = eps_growth_min
    if div_yield_min > 0: filters["dividend_yield_min"] = div_yield_min
    if cap_min > 0: filters["market_cap_min"] = cap_min
    if cap_max > 0: filters["market_cap_max"] = cap_max

    progress = st.progress(0, text="データ取得中...")
    df: pd.DataFrame = screen_stocks(
        "US", filters,
        sort_by=sort_options[sort_label],
        sort_desc=sort_desc,
        limit=50,
        progress_bar=progress,
    )
    progress.empty()

    st.session_state["us_results"] = df

if "us_results" in st.session_state and not st.session_state["us_results"].empty:
    df = st.session_state["us_results"]
    st.success(f"**{len(df)} 銘柄** が条件に合致しました")

    selected = render_screening_table(df, "US")

    if selected:
        st.markdown("---")
        render_stock_detail(selected, "US")

elif "us_results" in st.session_state:
    st.warning("条件に合致する銘柄が見つかりませんでした。条件を緩めてお試しください。")
else:
    st.info("👈 左のサイドバーで条件を設定して「スクリーニング実行」を押してください。\n\n条件を空のまま実行すると全銘柄を時価総額順で表示します。")

    with st.expander("💡 米国株スクリーニングのヒント"):
        st.markdown("""
        | 戦略 | 推奨設定 |
        |------|---------|
        | **QGV (Quality Growth Value)** | P/E上限 25 / ROE最低 15% / 売上高成長率最低 10% |
        | **ディフェンシブ高配当** | 配当利回り最低 3% / D/E最大 1.5 / 営業利益率最低 15% |
        | **成長株 (GARP)** | P/E上限 30 / EPS成長率最低 15% / 営業利益率最低 10% |
        | **バリュー株** | P/E上限 15 / P/B上限 2 / ROE最低 10% |
        """)
