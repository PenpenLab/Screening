"""
AI analysis service using Anthropic Claude API with prompt caching.
"""
import json
from anthropic import AsyncAnthropic
from cachetools import TTLCache

from app.models.stock import AIAnalysisRequest, AIAnalysisResponse, StockDetail
from app.config import get_settings

settings = get_settings()

_ai_cache: TTLCache = TTLCache(maxsize=200, ttl=86400)  # 24h cache for AI results

SYSTEM_PROMPT = """あなたはプロフェッショナルな株式アナリストです。与えられた財務データをもとに、投資家向けの客観的な分析レポートを提供します。

分析の際は以下の点を遵守してください:
1. 財務データに基づいた客観的な分析を行う
2. 強み・リスクをバランスよく提示する
3. 投資助言ではなく情報提供であることを明記する
4. 業界平均や競合との比較視点を含める
5. 短期・中長期の両視点を考慮する

必ず以下のJSON形式で回答してください:
{
  "summary": "200文字以内の総合サマリー",
  "strengths": ["強み1", "強み2", "強み3"],
  "risks": ["リスク1", "リスク2", "リスク3"],
  "verdict": "bullish | neutral | bearish",
  "verdict_reason": "判断理由（100文字以内）",
  "disclaimer": "投資助言ではなく情報提供目的です。投資判断はご自身の責任で行ってください。"
}"""

SYSTEM_PROMPT_EN = """You are a professional stock analyst. Based on the provided financial data, you provide objective analysis reports for investors.

Please adhere to the following:
1. Conduct objective analysis based on financial data
2. Present strengths and risks in a balanced manner
3. Note that this is information provision, not investment advice
4. Include comparison with industry averages and competitors
5. Consider both short-term and medium-to-long-term perspectives

Always respond in the following JSON format:
{
  "summary": "Overall summary within 200 characters",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "risks": ["Risk 1", "Risk 2", "Risk 3"],
  "verdict": "bullish | neutral | bearish",
  "verdict_reason": "Reason for verdict (within 100 characters)",
  "disclaimer": "This is for informational purposes only, not investment advice. Please make investment decisions at your own responsibility."
}"""


def _format_metrics(detail: StockDetail, market: str, language: str) -> str:
    currency_sym = "¥" if market == "JP" else "$"
    cap = f"{detail.market_cap / 1e12:.2f}兆{currency_sym}" if detail.market_cap and detail.market_cap >= 1e12 else (
        f"{detail.market_cap / 1e9:.1f}十億{currency_sym}" if detail.market_cap else "N/A"
    )

    lines = [
        f"銘柄: {detail.name} ({detail.symbol})",
        f"市場: {'東京証券取引所' if market == 'JP' else 'US市場'}",
        f"セクター: {detail.sector or 'N/A'} / {detail.industry or 'N/A'}",
        f"株価: {currency_sym}{detail.price or 'N/A'}",
        f"時価総額: {cap}",
        "",
        "--- バリュエーション ---",
        f"PER: {detail.per:.1f}倍" if detail.per else "PER: N/A",
        f"PBR: {detail.pbr:.2f}倍" if detail.pbr else "PBR: N/A",
        f"EV/EBITDA: {detail.ev_ebitda:.1f}倍" if detail.ev_ebitda else "EV/EBITDA: N/A",
        f"PEGレシオ: {detail.peg_ratio:.2f}" if detail.peg_ratio else "",
        "",
        "--- 収益性 ---",
        f"ROE: {detail.roe:.1f}%" if detail.roe else "ROE: N/A",
        f"ROA: {detail.roa:.1f}%" if detail.roa else "ROA: N/A",
        f"営業利益率: {detail.operating_margin:.1f}%" if detail.operating_margin else "営業利益率: N/A",
        f"純利益率: {detail.net_margin:.1f}%" if detail.net_margin else "純利益率: N/A",
        "",
        "--- 成長性 ---",
        f"売上高成長率(YoY): {detail.revenue_growth:.1f}%" if detail.revenue_growth else "売上高成長率: N/A",
        f"利益成長率(YoY): {detail.earnings_growth:.1f}%" if detail.earnings_growth else "利益成長率: N/A",
        "",
        "--- 財務健全性 ---",
        f"D/Eレシオ: {detail.debt_to_equity:.2f}" if detail.debt_to_equity else "D/Eレシオ: N/A",
        f"流動比率: {detail.current_ratio:.2f}" if detail.current_ratio else "流動比率: N/A",
        f"自己資本比率: {detail.equity_ratio:.1f}%" if detail.equity_ratio else "自己資本比率: N/A",
        "",
        "--- 株主還元 ---",
        f"配当利回り: {detail.dividend_yield:.2f}%" if detail.dividend_yield else "配当利回り: N/A",
        f"配当性向: {detail.payout_ratio:.1f}%" if detail.payout_ratio else "配当性向: N/A",
        "",
        "--- アナリスト ---",
        f"目標株価: {currency_sym}{detail.target_price:.0f}" if detail.target_price else "目標株価: N/A",
        f"推奨: {detail.recommendation or 'N/A'}",
    ]

    if detail.description:
        lines += ["", "--- 事業概要 ---", detail.description[:500]]

    return "\n".join(line for line in lines if line is not None)


async def analyze_stock(
    request: AIAnalysisRequest,
    detail: StockDetail,
) -> AIAnalysisResponse:
    cache_key = f"ai:{request.market}:{request.symbol}:{request.language}"
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    system_prompt = SYSTEM_PROMPT if request.language == "ja" else SYSTEM_PROMPT_EN
    metrics_text = _format_metrics(detail, request.market, request.language)

    user_message = f"以下の財務データを分析してください:\n\n{metrics_text}" if request.language == "ja" else \
        f"Please analyze the following financial data:\n\n{metrics_text}"

    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},  # Prompt caching
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()
    # Extract JSON from response
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    data = json.loads(raw)
    result = AIAnalysisResponse(
        symbol=request.symbol,
        summary=data.get("summary", ""),
        strengths=data.get("strengths", []),
        risks=data.get("risks", []),
        verdict=data.get("verdict", "neutral"),
        verdict_reason=data.get("verdict_reason", ""),
        disclaimer=data.get("disclaimer", "投資助言ではなく情報提供目的です。"),
    )
    _ai_cache[cache_key] = result
    return result
