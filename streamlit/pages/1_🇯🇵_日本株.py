"""
日本株スクリーニングページ
"""
import streamlit as st
import pandas as pd

from screening_service import screen_stocks
from ui_components import render_screening_table, render_stock_detail

st.set_page_config(page_title="日本株スクリーニング", page_icon="🇯🇵", layout="wide")

st.title("🇯🇵 日本株スクリーニング")
st.caption("東証上場銘柄 · 日本株特有の指標でフィルタリング")

# ── サイドバー: フィルター ────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 スクリーニング条件")

    st.subheader("バリュエーション")
    per_col1, per_col2 = st.columns(2)
    per_min = per_col1.number_input("PER 下限", min_value=0.0, value=0.0, step=1.0, format="%.1f")
    per_max = per_col2.number_input("PER 上限", min_value=0.0, value=0.0, step=1.0, format="%.1f",
                                     help="0 = 上限なし")
    pbr_col1, pbr_col2 = st.columns(2)
    pbr_min = pbr_col1.number_input("PBR 下限", min_value=0.0, value=0.0, step=0.1, format="%.2f")
    pbr_max = pbr_col2.number_input("PBR 上限", min_value=0.0, value=0.0, step=0.1, format="%.2f",
                                     help="0 = 上限なし")

    st.subheader("収益性")
    roe_min = st.number_input("ROE 最低 (%)", min_value=0.0, value=0.0, step=1.0, format="%.1f")
    roa_min = st.number_input("ROA 最低 (%)", min_value=0.0, value=0.0, step=1.0, format="%.1f")
    op_margin_min = st.number_input("営業利益率 最低 (%)", min_value=0.0, value=0.0, step=1.0)

    st.subheader("財務健全性")
    equity_ratio_min = st.number_input("自己資本比率 最低 (%)", min_value=0.0, value=0.0, step=5.0,
                                        help="40%以上が安全圏の目安")

    st.subheader("成長性")
    rev_growth_min = st.number_input("売上高成長率 最低 (%)", value=0.0, step=1.0)

    st.subheader("株主還元")
    div_yield_min = st.number_input("配当利回り 最低 (%)", min_value=0.0, value=0.0, step=0.5, format="%.1f")

    st.subheader("時価総額")
    cap_col1, cap_col2 = st.columns(2)
    cap_min = cap_col1.number_input("下限 (十億¥)", min_value=0.0, value=0.0, step=100.0)
    cap_max = cap_col2.number_input("上限 (十億¥)", min_value=0.0, value=0.0, step=100.0,
                                     help="0 = 上限なし")

    st.subheader("並び替え")
    sort_options = {
        "時価総額": "market_cap", "PER": "per", "PBR": "pbr",
        "ROE": "roe", "配当利回り": "dividend_yield",
        "自己資本比率": "equity_ratio", "売上高成長率": "revenue_growth",
        "営業利益率": "operating_margin",
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
    if roa_min > 0: filters["roa_min"] = roa_min
    if op_margin_min > 0: filters["operating_margin_min"] = op_margin_min
    if equity_ratio_min > 0: filters["equity_ratio_min"] = equity_ratio_min
    if rev_growth_min != 0: filters["revenue_growth_min"] = rev_growth_min
    if div_yield_min > 0: filters["dividend_yield_min"] = div_yield_min
    if cap_min > 0: filters["market_cap_min"] = cap_min
    if cap_max > 0: filters["market_cap_max"] = cap_max

    progress = st.progress(0, text="データ取得中...")
    df: pd.DataFrame = screen_stocks(
        "JP", filters,
        sort_by=sort_options[sort_label],
        sort_desc=sort_desc,
        limit=50,
        progress_bar=progress,
    )
    progress.empty()
    st.session_state["jp_results"] = df

if "jp_results" in st.session_state and not st.session_state["jp_results"].empty:
    df = st.session_state["jp_results"]
    st.success(f"**{len(df)} 銘柄** が条件に合致しました")
    selected = render_screening_table(df, "JP")
    if selected:
        st.markdown("---")
        render_stock_detail(selected, "JP")

elif "jp_results" in st.session_state:
    st.warning("条件に合致する銘柄が見つかりませんでした。条件を緩めてお試しください。")
else:
    st.info("👈 左のサイドバーで条件を設定して「スクリーニング実行」を押してください。\n\n条件を空のまま実行すると全銘柄を時価総額順で表示します。")
    with st.expander("💡 日本株スクリーニングのヒント"):
        st.markdown("""
        | 戦略 | 推奨設定 |
        |------|---------|
        | **高配当バリュー株** | PBR上限 1.5 / 配当利回り最低 3% / 自己資本比率最低 40% |
        | **ROE重視 (バフェット流)** | ROE最低 15% / PBR上限 3 / 自己資本比率最低 30% |
        | **成長株** | 売上高成長率最低 10% / ROE最低 10% / 時価総額下限 100B |
        | **財務健全 バリュー** | PER上限 15 / PBR上限 1 / 自己資本比率最低 50% |
        """)
