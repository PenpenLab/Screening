"""
共通UIコンポーネント (Streamlit)
"""
from __future__ import annotations

import json
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from stock_service import fetch_info, fetch_history, build_metrics
from ai_service import analyze_stock


# ── フォーマット ───────────────────────────────────────────────────────────

def fmt_num(v, digits=1, suffix="", prefix="") -> str:
    if v is None:
        return "—"
    return f"{prefix}{v:.{digits}f}{suffix}"


def fmt_price(price, currency) -> str:
    if price is None:
        return "—"
    sym = "¥" if currency == "JPY" else "$"
    if currency == "JPY":
        return f"{sym}{price:,.0f}"
    return f"{sym}{price:.2f}"


def fmt_cap(cap, currency) -> str:
    if cap is None:
        return "—"
    sym = "¥" if currency == "JPY" else "$"
    if cap >= 1e12:
        return f"{sym}{cap/1e12:.2f}T"
    if cap >= 1e9:
        return f"{sym}{cap/1e9:.1f}B"
    if cap >= 1e6:
        return f"{sym}{cap/1e6:.0f}M"
    return f"{sym}{cap:,.0f}"


def delta_color(v) -> str:
    if v is None:
        return "off"
    return "normal" if v >= 0 else "inverse"


# ── 株価チャート ──────────────────────────────────────────────────────────

PERIOD_OPTIONS = {"1ヶ月": "1mo", "3ヶ月": "3mo", "6ヶ月": "6mo",
                  "1年": "1y", "2年": "2y", "5年": "5y"}


def render_price_chart(symbol: str, market: str, currency: str):
    period_label = st.radio(
        "期間", list(PERIOD_OPTIONS.keys()),
        index=3, horizontal=True, key=f"period_{symbol}",
    )
    period = PERIOD_OPTIONS[period_label]

    with st.spinner("チャート取得中..."):
        hist = fetch_history(symbol, market, period)

    if hist.empty:
        st.warning("株価データを取得できませんでした。")
        return

    is_up = hist["Close"].iloc[-1] >= hist["Close"].iloc[0]
    color = "#22c55e" if is_up else "#ef4444"
    fill_rgb = "34,197,94" if is_up else "239,68,68"
    fill_color = f"rgba({fill_rgb},0.15)"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist["Close"],
        mode="lines",
        fill="tozeroy",
        line=dict(color=color, width=2),
        fillcolor=fill_color,
        name="終値",
    ))

    price_sym = "¥" if currency == "JPY" else "$"
    fig.update_layout(
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#94a3b8"),
        margin=dict(l=0, r=0, t=0, b=0),
        height=280,
        xaxis=dict(showgrid=False, color="#475569"),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", color="#475569",
                   tickprefix=price_sym),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── 銘柄詳細パネル ────────────────────────────────────────────────────────

def render_stock_detail(symbol: str, market: str):
    with st.spinner(f"{symbol} のデータを取得中..."):
        info = fetch_info(symbol, market)
        m = build_metrics(symbol, market, info)

    currency = m["currency"]
    price_sym = "¥" if currency == "JPY" else "$"

    st.subheader(f"{m['name']}  `{symbol}`")
    col_p, col_chg, col_cap, col_52 = st.columns(4)
    col_p.metric("株価", fmt_price(m["price"], currency),
                 f"{m['change_pct']:+.2f}%" if m["change_pct"] else None,
                 delta_color=delta_color(m["change_pct"]))
    col_chg.metric("時価総額", fmt_cap(m["market_cap"], currency))
    col_cap.metric("52週 高値", fmt_price(m["week52_high"], currency))
    col_52.metric("52週 安値", fmt_price(m["week52_low"], currency))

    render_price_chart(symbol, market, currency)

    st.markdown("---")
    tab_val, tab_prof, tab_health = st.tabs(["📊 バリュエーション", "📈 収益性・成長性", "🏦 財務・株主還元"])

    with tab_val:
        c1, c2, c3 = st.columns(3)
        c1.metric("PER", fmt_num(m["per"], 1, "x"))
        c2.metric("PBR", fmt_num(m["pbr"], 2, "x"))
        c3.metric("EV/EBITDA", fmt_num(m["ev_ebitda"], 1, "x"))
        c1.metric("PSR", fmt_num(m["psr"], 2, "x"))
        c2.metric("PEGレシオ", fmt_num(m["peg_ratio"], 2))
        c3.metric("EPS", f"{price_sym}{m['eps']:.2f}" if m["eps"] else "—")

    with tab_prof:
        c1, c2, c3 = st.columns(3)
        c1.metric("ROE", fmt_num(m["roe"], 1, "%"))
        c2.metric("ROA", fmt_num(m["roa"], 1, "%"))
        c3.metric("営業利益率", fmt_num(m["operating_margin"], 1, "%"))
        c1.metric("純利益率", fmt_num(m["net_margin"], 1, "%"))
        c2.metric("売上高成長率", fmt_num(m["revenue_growth"], 1, "%"))
        c3.metric("利益成長率", fmt_num(m["earnings_growth"], 1, "%"))

    with tab_health:
        c1, c2, c3 = st.columns(3)
        c1.metric("自己資本比率" if market == "JP" else "D/E Ratio",
                  fmt_num(m["equity_ratio"], 1, "%") if market == "JP" else fmt_num(m["debt_to_equity"], 2))
        c2.metric("流動比率", fmt_num(m["current_ratio"], 2))
        c3.metric("配当利回り", fmt_num(m["dividend_yield"], 2, "%"))
        c1.metric("配当性向", fmt_num(m["payout_ratio"], 1, "%"))
        c2.metric("目標株価",
                  f"{price_sym}{m['target_price']:.0f}" if m["target_price"] else "—")
        c3.metric("推奨", m.get("recommendation") or "—")

    if m.get("description"):
        with st.expander("会社概要"):
            st.write(m["description"][:800])
            cols = st.columns(3)
            if m.get("employees"):
                cols[0].write(f"👥 {m['employees']:,} 名")
            if m.get("country"):
                cols[1].write(f"🌏 {m['country']}")
            if m.get("website"):
                cols[2].markdown(f"[🔗 公式サイト]({m['website']})")

    st.markdown("---")
    st.subheader("🤖 Claude AI 分析")

    has_key = bool(st.secrets.get("ANTHROPIC_API_KEY", ""))
    if not has_key:
        st.info("AI分析を使用するには Streamlit Cloud の Secrets に `ANTHROPIC_API_KEY` を設定してください。")
        return

    if st.button("AI 分析を実行", key=f"ai_{symbol}", type="primary"):
        with st.spinner("Claude が分析中..."):
            try:
                result = analyze_stock(symbol, market, json.dumps(m))
                _render_ai_result(result)
            except Exception as e:
                st.error(f"AI分析に失敗しました: {e}")


def _render_ai_result(result: dict):
    verdict = result.get("verdict", "neutral")
    icons = {"bullish": "🟢", "neutral": "🟡", "bearish": "🔴"}
    labels = {"bullish": "強気 (Bullish)", "neutral": "中立 (Neutral)", "bearish": "弱気 (Bearish)"}

    st.markdown(f"### {icons.get(verdict, '🟡')} {labels.get(verdict, verdict)}")
    st.caption(result.get("verdict_reason", ""))
    st.write(result.get("summary", ""))

    col_s, col_r = st.columns(2)
    with col_s:
        st.markdown("**✅ 強み**")
        for s in result.get("strengths", []):
            st.markdown(f"- {s}")
    with col_r:
        st.markdown("**⚠️ リスク**")
        for r in result.get("risks", []):
            st.markdown(f"- {r}")

    st.caption(result.get("disclaimer", ""))


# ── スクリーニング結果テーブル ─────────────────────────────────────────────

JP_DISPLAY_COLS = {
    "name": "銘柄名", "symbol": "コード", "price": "株価",
    "change_pct": "前日比%", "market_cap": "時価総額",
    "per": "PER", "pbr": "PBR", "roe": "ROE%",
    "operating_margin": "営業利益率%", "dividend_yield": "配当利回り%",
    "equity_ratio": "自己資本比率%", "sector": "セクター",
}

US_DISPLAY_COLS = {
    "name": "Name", "symbol": "Ticker", "price": "Price",
    "change_pct": "Chg%", "market_cap": "Mkt Cap",
    "per": "P/E", "pbr": "P/B", "roe": "ROE%",
    "operating_margin": "Op.Margin%", "dividend_yield": "Div.Yield%",
    "revenue_growth": "Rev.Growth%", "sector": "Sector",
}


def render_screening_table(df: pd.DataFrame, market: str) -> str | None:
    col_map = JP_DISPLAY_COLS if market == "JP" else US_DISPLAY_COLS
    available = [c for c in col_map if c in df.columns]
    display_df = df[available].copy().rename(columns=col_map)

    currencies = df["currency"].tolist() if "currency" in df.columns else None

    # 株価・時価総額: 通貨記号付きフォーマット
    for disp_col, raw_col, fmt_fn in [
        ("株価", "price", fmt_price), ("Price", "price", fmt_price),
        ("時価総額", "market_cap", fmt_cap), ("Mkt Cap", "market_cap", fmt_cap),
    ]:
        if disp_col in display_df.columns and raw_col in df.columns and currencies:
            display_df[disp_col] = [fmt_fn(v, c) for v, c in zip(df[raw_col], currencies)]

    # 前日比: +/- 符号付き %
    for col in ["前日比%", "Chg%"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda v: f"{v:+.2f}%" if pd.notna(v) else "—"
            )

    for col in ["PER", "PBR", "P/E", "P/B"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda v: f"{v:.1f}x" if pd.notna(v) else "—")
    for col in ["ROE%", "営業利益率%", "配当利回り%", "自己資本比率%",
                "Op.Margin%", "Div.Yield%", "Rev.Growth%"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda v: f"{v:.1f}%" if pd.notna(v) else "—")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    symbols = df["symbol"].tolist()
    selected = st.selectbox("詳細を表示する銘柄を選択", ["— 選択してください —"] + symbols,
                            key=f"select_{market}")
    return selected if selected != "— 選択してください —" else None
