"""
Claude AI 分析サービス (Streamlit用)
prompt caching でコスト最適化
"""
from __future__ import annotations

import json
import streamlit as st
from anthropic import Anthropic

SYSTEM_PROMPT = """あなたはプロフェッショナルな株式アナリストです。与えられた財務データをもとに、投資家向けの客観的な分析レポートを提供します。

分析の際は以下の点を遵守してください:
1. 財務データに基づいた客観的な分析を行う
2. 強み・リスクをバランスよく提示する
3. 投資助言ではなく情報提供であることを明記する
4. 業界平均や競合との比較視点を含める
5. 短期・中長期・長期の3つの時間軸で売買タイミングを判断する

timingフィールドの定義:
- short_term: 1〜4週間の目線。テクニカル・需給・直近の値動きを重視
- mid_term: 1〜6ヶ月の目線。業績モメンタム・セクタートレンドを重視
- long_term: 1年以上の目線。ビジネスモデルの競争優位性・財務健全性を重視
各actionは "買い" / "売り" / "様子見" のいずれかとする。

必ず以下のJSON形式で回答してください:
{
  "summary": "200文字以内の総合サマリー",
  "strengths": ["強み1", "強み2", "強み3"],
  "risks": ["リスク1", "リスク2", "リスク3"],
  "verdict": "bullish | neutral | bearish",
  "verdict_reason": "判断理由（100文字以内）",
  "timing": {
    "short_term": {"action": "買い | 売り | 様子見", "reason": "根拠（60文字以内）"},
    "mid_term":   {"action": "買い | 売り | 様子見", "reason": "根拠（60文字以内）"},
    "long_term":  {"action": "買い | 売り | 様子見", "reason": "根拠（60文字以内）"}
  },
  "disclaimer": "投資助言ではなく情報提供目的です。投資判断はご自身の責任で行ってください。"
}"""


def _format_metrics(m: dict) -> str:
    currency_sym = "¥" if m.get("currency") == "JPY" else "$"
    cap = m.get("market_cap")
    if cap:
        cap_str = f"{cap/1e12:.2f}兆{currency_sym}" if cap >= 1e12 else f"{cap/1e9:.1f}十億{currency_sym}"
    else:
        cap_str = "N/A"

    def fmt(v, suffix="", digits=1):
        return f"{v:.{digits}f}{suffix}" if v is not None else "N/A"

    return f"""銘柄: {m.get('name')} ({m.get('symbol')})
市場: {'東京証券取引所' if m.get('market') == 'JP' else 'US市場'}
セクター: {m.get('sector') or 'N/A'} / {m.get('industry') or 'N/A'}
株価: {currency_sym}{m.get('price') or 'N/A'}
時価総額: {cap_str}

--- バリュエーション ---
PER: {fmt(m.get('per'), '倍')}
PBR: {fmt(m.get('pbr'), '倍', 2)}
EV/EBITDA: {fmt(m.get('ev_ebitda'), '倍')}
PEGレシオ: {fmt(m.get('peg_ratio'), '', 2)}

--- 収益性 ---
ROE: {fmt(m.get('roe'), '%')}
ROA: {fmt(m.get('roa'), '%')}
営業利益率: {fmt(m.get('operating_margin'), '%')}
純利益率: {fmt(m.get('net_margin'), '%')}

--- 成長性 ---
売上高成長率(YoY): {fmt(m.get('revenue_growth'), '%')}
利益成長率(YoY): {fmt(m.get('earnings_growth'), '%')}

--- 財務健全性 ---
D/Eレシオ: {fmt(m.get('debt_to_equity'), '', 2)}
流動比率: {fmt(m.get('current_ratio'), '', 2)}
自己資本比率: {fmt(m.get('equity_ratio'), '%')}

--- 株主還元 ---
配当利回り: {fmt(m.get('dividend_yield'), '%', 2)}
配当性向: {fmt(m.get('payout_ratio'), '%')}

--- アナリスト ---
目標株価: {currency_sym + str(round(m['target_price'])) if m.get('target_price') else 'N/A'}
推奨: {m.get('recommendation') or 'N/A'}

--- 事業概要 ---
{(m.get('description') or '')[:500]}"""


@st.cache_data(ttl=86400, show_spinner=False)
def analyze_stock(symbol: str, market: str, metrics_json: str) -> dict:
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY が設定されていません")

    metrics = json.loads(metrics_json)
    client = Anthropic(api_key=api_key)
    metrics_text = _format_metrics(metrics)
    user_message = f"以下の財務データを分析してください:\n\n{metrics_text}"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    return json.loads(raw)


@st.cache_data(ttl=86400, show_spinner=False)
def analyze_stock_full(symbol: str, market: str, metrics_json: str, technical_summary: str) -> dict:
    """テクニカルシグナルを含む総合分析（銘柄分析ページ用）"""
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY が設定されていません")

    metrics = json.loads(metrics_json)
    client = Anthropic(api_key=api_key)
    metrics_text = _format_metrics(metrics)
    user_message = (
        f"以下の財務データとテクニカル分析をもとに総合分析してください。\n\n"
        f"{metrics_text}\n\n"
        f"--- テクニカルシグナル ---\n{technical_summary}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    return json.loads(raw)
