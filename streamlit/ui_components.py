"""
共通UIコンポーネント (Streamlit)
"""
from __future__ import annotations

import json
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import yfinance as yf

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
                 f"{m['change_pct']:+.2f}%" if m["change_pct"] is not None else None,
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
        c3.metric("EPS", f"{price_sym}{m['eps']:.2f}" if m["eps"] is not None else "—")

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
                  f"{price_sym}{m['target_price']:.0f}" if m["target_price"] is not None else "—")
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


# ── 銘柄分析ページ用コンポーネント ────────────────────────────────────────

def _dark_layout(fig, title: str = "", height: int = 250):
    fig.update_layout(
        title=title,
        plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
        font=dict(color="#94a3b8"),
        height=height, margin=dict(l=0, r=0, t=30 if title else 10, b=0),
        xaxis=dict(showgrid=False, color="#475569"),
        yaxis=dict(gridcolor="#1e293b", color="#475569"),
    )


def render_fundamental_tab(m: dict, fin_data: dict):
    currency = m["currency"]
    unit = "億円" if currency == "JPY" else "B USD"
    divisor = 1e8 if currency == "JPY" else 1e9

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROE", fmt_num(m["roe"], 1, "%"))
    c2.metric("営業利益率", fmt_num(m["operating_margin"], 1, "%"))
    c3.metric("配当利回り", fmt_num(m["dividend_yield"], 2, "%"))
    c4.metric("PER", fmt_num(m["per"], 1, "x"))

    income = fin_data.get("income", pd.DataFrame())
    if income is None or income.empty:
        st.info("財務諸表データを取得できませんでした。")
        return

    income = income.sort_index(axis=1)

    if "Total Revenue" in income.index:
        rev = income.loc["Total Revenue"].dropna() / divisor
        if not rev.empty:
            fig = go.Figure(go.Bar(
                x=[str(d)[:7] for d in rev.index], y=rev.values,
                marker_color="#3b82f6",
                text=[f"{v:.0f}" for v in rev.values], textposition="outside",
            ))
            _dark_layout(fig, f"売上高推移 ({unit})", height=250)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    col_a, col_b = st.columns(2)
    for widget, row_key, label, color in [
        (col_a, "Operating Income", f"営業利益 ({unit})", "#22c55e"),
        (col_b, "Net Income", f"純利益 ({unit})", "#a855f7"),
    ]:
        if row_key in income.index:
            series = income.loc[row_key].dropna() / divisor
            if not series.empty:
                bar_colors = ["#22c55e" if v >= 0 else "#ef4444" for v in series.values]
                fig = go.Figure(go.Bar(
                    x=[str(d)[:7] for d in series.index], y=series.values,
                    marker_color=bar_colors,
                ))
                _dark_layout(fig, label, height=220)
                widget.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_technical_tab(indicators: dict, m: dict):
    if not indicators:
        st.warning("価格データを取得できませんでした。")
        return

    price_sym = "¥" if m["currency"] == "JPY" else "$"
    signals = indicators.get("signals", [])
    bullish = sum(1 for s in signals if s[2] == "bullish")
    bearish = sum(1 for s in signals if s[2] == "bearish")

    if bullish > bearish:
        overall, border = "🟢 買い優勢", "#22c55e"
    elif bearish > bullish:
        overall, border = "🔴 売り優勢", "#ef4444"
    else:
        overall, border = "🟡 中立", "#f59e0b"

    rows_html = "".join(
        f"<div style='margin:4px 0'>{'🟢' if s[2]=='bullish' else '🔴' if s[2]=='bearish' else '🟡'} "
        f"<b>{s[0]}</b> &mdash; {s[1]}</div>"
        for s in signals
    )
    st.markdown(
        f"""<div style="border:2px solid {border};border-radius:8px;padding:14px;margin-bottom:12px">
<span style="font-size:1.15em;font-weight:bold">{overall}</span>
&nbsp;&nbsp;<span style="color:#94a3b8;font-size:.9em">買い {bullish} / 売り {bearish} / 計 {len(signals)} シグナル</span>
<hr style="border-color:#1e293b;margin:8px 0">
{rows_html}
</div>""",
        unsafe_allow_html=True,
    )

    close = indicators["close"]
    ma20, ma50, ma200 = indicators["ma20"], indicators["ma50"], indicators["ma200"]
    rsi = indicators["rsi"]
    macd_line = indicators["macd_line"]
    signal_line = indicators["signal_line"]
    histogram = indicators["histogram"]
    latest_rsi = indicators.get("latest_rsi")

    is_up = float(close.iloc[-1]) >= float(close.iloc[0])
    price_color = "#22c55e" if is_up else "#ef4444"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=close.index, y=close, mode="lines",
                             line=dict(color=price_color, width=2), name="株価"))
    fig.add_trace(go.Scatter(x=ma20.index, y=ma20, mode="lines",
                             line=dict(color="#60a5fa", width=1, dash="dot"), name="MA20"))
    fig.add_trace(go.Scatter(x=ma50.index, y=ma50, mode="lines",
                             line=dict(color="#f59e0b", width=1, dash="dot"), name="MA50"))
    fig.add_trace(go.Scatter(x=ma200.index, y=ma200, mode="lines",
                             line=dict(color="#a78bfa", width=1.5), name="MA200"))
    _dark_layout(fig, height=300)
    fig.update_layout(
        yaxis=dict(tickprefix=price_sym, gridcolor="#1e293b"),
        legend=dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    col_rsi, col_macd = st.columns(2)
    with col_rsi:
        rsi_color = ("#ef4444" if latest_rsi and latest_rsi > 70
                     else "#22c55e" if latest_rsi and latest_rsi < 30 else "#60a5fa")
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(x=rsi.index, y=rsi, mode="lines",
                                   line=dict(color=rsi_color, width=2), name="RSI"))
        fig_r.add_hline(y=70, line_color="#ef4444", line_dash="dash", line_width=1,
                        annotation_text="買われすぎ 70", annotation_font_color="#ef4444")
        fig_r.add_hline(y=30, line_color="#22c55e", line_dash="dash", line_width=1,
                        annotation_text="売られすぎ 30", annotation_font_color="#22c55e")
        fig_r.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,0.08)", line_width=0)
        fig_r.add_hrect(y0=0, y1=30, fillcolor="rgba(34,197,94,0.08)", line_width=0)
        _dark_layout(fig_r, f"RSI(14) 現在: {latest_rsi:.1f}" if latest_rsi else "RSI(14)", height=230)
        fig_r.update_layout(yaxis=dict(range=[0, 100], gridcolor="#1e293b"))
        st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})

    with col_macd:
        hist_colors = ["#22c55e" if v >= 0 else "#ef4444" for v in histogram.values]
        fig_m = go.Figure()
        fig_m.add_trace(go.Bar(x=histogram.index, y=histogram.values,
                               marker_color=hist_colors, name="ヒスト", opacity=0.6))
        fig_m.add_trace(go.Scatter(x=macd_line.index, y=macd_line, mode="lines",
                                   line=dict(color="#60a5fa", width=1.5), name="MACD"))
        fig_m.add_trace(go.Scatter(x=signal_line.index, y=signal_line, mode="lines",
                                   line=dict(color="#f97316", width=1.5), name="Signal"))
        _dark_layout(fig_m, "MACD(12,26,9)", height=230)
        fig_m.update_layout(
            legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)", font=dict(size=10))
        )
        st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar": False})


def render_market_tab(m: dict, info: dict, holders: pd.DataFrame):
    col_short, col_macro = st.columns(2)

    with col_short:
        st.subheader("需給データ")
        try:
            sp = float(info["shortPercentOfFloat"]) * 100 if info.get("shortPercentOfFloat") is not None else None
        except Exception:
            sp = None
        try:
            sr = float(info["shortRatio"]) if info.get("shortRatio") is not None else None
        except Exception:
            sr = None
        s1, s2 = st.columns(2)
        s1.metric("空売り比率", f"{sp:.1f}%" if sp is not None else "—",
                  help="流通株に対する空売り残高の割合（Short Float）")
        s2.metric("Days to Cover", f"{sr:.1f}日" if sr is not None else "—",
                  help="空売り残高を出来高で割った解消所要日数")
        if m.get("market") == "JP":
            st.caption("📌 信用買い残・売り残は別途APIが必要なため現在未対応です。")

    with col_macro:
        st.subheader("マクロ指標（現在値）")
        for label, sym in [
            ("米10年債利回り", "^TNX"),
            ("USD/JPY", "USDJPY=X"),
            ("VIX（恐怖指数）", "^VIX"),
        ]:
            try:
                price = yf.Ticker(sym).info.get("regularMarketPrice")
                st.metric(label, f"{float(price):.2f}" if price else "—")
            except Exception:
                st.metric(label, "—")

    st.markdown("---")
    st.subheader("🏛 機関投資家 保有上位")
    if holders is not None and not holders.empty:
        disp = [c for c in ["Holder", "Shares", "% Out", "Value"] if c in holders.columns]
        st.dataframe(holders[disp].head(10), use_container_width=True, hide_index=True)
    else:
        st.info("機関投資家データを取得できませんでした（日本株は対応外の場合があります）。")
