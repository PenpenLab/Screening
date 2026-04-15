"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Bot, TrendingUp, TrendingDown, Minus, AlertTriangle, CheckCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { Market } from "@/types/stock";

interface Props {
  symbol: string;
  market: Market;
}

const VERDICT_STYLES = {
  bullish: {
    bg: "bg-green-950/50 border-green-800",
    text: "text-green-400",
    icon: TrendingUp,
    label: "強気 (Bullish)",
  },
  neutral: {
    bg: "bg-slate-800/50 border-slate-700",
    text: "text-slate-300",
    icon: Minus,
    label: "中立 (Neutral)",
  },
  bearish: {
    bg: "bg-red-950/50 border-red-800",
    text: "text-red-400",
    icon: TrendingDown,
    label: "弱気 (Bearish)",
  },
};

export function AIAnalysisPanel({ symbol, market }: Props) {
  const [enabled, setEnabled] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["ai-analysis", market, symbol],
    queryFn: () => api.analyzeAI(symbol, market, "ja"),
    enabled,
    staleTime: Infinity,
  });

  if (!enabled) {
    return (
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 text-center">
        <Bot className="w-8 h-8 text-blue-400 mx-auto mb-2" />
        <p className="text-slate-400 text-sm mb-3">
          Claude AI による財務分析レポートを生成します
        </p>
        <button
          onClick={() => setEnabled(true)}
          className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          AI 分析を開始
        </button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-5">
        <div className="flex items-center gap-2 text-blue-400 mb-3">
          <Bot className="w-5 h-5 animate-pulse" />
          <span className="text-sm font-medium">Claude が分析中...</span>
        </div>
        <div className="space-y-2">
          {[100, 80, 60].map((w) => (
            <div key={w} className={`h-3 bg-slate-800 rounded animate-pulse w-${w === 100 ? "full" : `${w}/100 `}`} style={{ width: `${w}%` }} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-slate-900 rounded-xl border border-red-900 p-4 text-red-400 text-sm">
        AI分析の取得に失敗しました。ANTHROPIC_API_KEY の設定を確認してください。
      </div>
    );
  }

  const style = VERDICT_STYLES[data.verdict] ?? VERDICT_STYLES.neutral;
  const VerdictIcon = style.icon;

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Bot className="w-5 h-5 text-blue-400" />
        <h3 className="font-semibold text-white">AI 分析レポート</h3>
        <span className="text-xs text-slate-500 ml-auto">by Claude</span>
      </div>

      {/* Verdict */}
      <div className={`rounded-lg border p-3 ${style.bg}`}>
        <div className={`flex items-center gap-2 font-semibold ${style.text}`}>
          <VerdictIcon className="w-4 h-4" />
          {style.label}
        </div>
        <p className="text-sm text-slate-300 mt-1">{data.verdict_reason}</p>
      </div>

      {/* Summary */}
      <div>
        <p className="text-sm text-slate-300 leading-relaxed">{data.summary}</p>
      </div>

      {/* Strengths & Risks */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <div className="flex items-center gap-1 text-green-400 text-xs font-medium mb-2">
            <CheckCircle className="w-3 h-3" /> 強み
          </div>
          <ul className="space-y-1">
            {data.strengths.map((s, i) => (
              <li key={i} className="text-xs text-slate-300 flex gap-1.5">
                <span className="text-green-500 mt-0.5">•</span>
                {s}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <div className="flex items-center gap-1 text-red-400 text-xs font-medium mb-2">
            <AlertTriangle className="w-3 h-3" /> リスク
          </div>
          <ul className="space-y-1">
            {data.risks.map((r, i) => (
              <li key={i} className="text-xs text-slate-300 flex gap-1.5">
                <span className="text-red-500 mt-0.5">•</span>
                {r}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <p className="text-xs text-slate-600 border-t border-slate-800 pt-3">{data.disclaimer}</p>
    </div>
  );
}
