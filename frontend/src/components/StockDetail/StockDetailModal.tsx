"use client";

import { useQuery } from "@tanstack/react-query";
import { X, ExternalLink, Users, Globe } from "lucide-react";
import { api } from "@/lib/api";
import { formatNumber, formatMarketCap, formatPrice, colorClass } from "@/lib/utils";
import { PriceChart } from "@/components/StockChart/PriceChart";
import { AIAnalysisPanel } from "@/components/AIAnalysis/AIAnalysisPanel";
import type { Market } from "@/types/stock";

interface Props {
  symbol: string;
  market: Market;
  onClose: () => void;
}

interface MetricRowProps {
  label: string;
  value: React.ReactNode;
}

function MetricRow({ label, value }: MetricRowProps) {
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-slate-800/50">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-xs font-mono text-slate-200">{value}</span>
    </div>
  );
}

export function StockDetailModal({ symbol, market, onClose }: Props) {
  const { data, isLoading } = useQuery({
    queryKey: ["stock", market, symbol],
    queryFn: () => api.getStock(symbol, market),
  });

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-start justify-center p-4 overflow-y-auto">
      <div className="bg-slate-950 border border-slate-800 rounded-2xl w-full max-w-4xl my-8">
        {/* Header */}
        <div className="flex items-start justify-between p-5 border-b border-slate-800">
          <div>
            {isLoading ? (
              <div className="h-6 w-48 bg-slate-800 rounded animate-pulse" />
            ) : (
              <>
                <h2 className="text-xl font-bold text-white">{data?.name}</h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-sm text-slate-400">{symbol}</span>
                  <span className="text-slate-600">·</span>
                  <span className="text-sm text-slate-400">{data?.exchange}</span>
                  <span className="text-slate-600">·</span>
                  <span className="text-sm text-slate-400">{data?.sector}</span>
                </div>
              </>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-slate-500">データ読み込み中...</div>
        ) : data ? (
          <div className="p-5 space-y-5">
            {/* Price hero */}
            <div className="flex items-end gap-4">
              <div>
                <div className="text-3xl font-bold font-mono text-white">
                  {formatPrice(data.price, data.currency)}
                </div>
                <div className={`text-sm font-mono ${colorClass(data.change_pct)}`}>
                  {data.change_pct !== null
                    ? `${data.change_pct > 0 ? "+" : ""}${data.change_pct.toFixed(2)}%`
                    : "—"}
                </div>
              </div>
              <div className="ml-auto text-right">
                <div className="text-xs text-slate-500">時価総額</div>
                <div className="text-sm font-mono">{formatMarketCap(data.market_cap, data.currency)}</div>
              </div>
              {data.week52_high && data.week52_low && (
                <div className="text-right">
                  <div className="text-xs text-slate-500">52週レンジ</div>
                  <div className="text-sm font-mono text-slate-300">
                    {formatPrice(data.week52_low, data.currency)} – {formatPrice(data.week52_high, data.currency)}
                  </div>
                </div>
              )}
            </div>

            {/* Chart */}
            <PriceChart symbol={symbol} market={market} currency={data.currency} />

            {/* Metrics grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Valuation */}
              <div className="bg-slate-900 rounded-xl p-4">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">バリュエーション</h4>
                <MetricRow label="PER" value={formatNumber(data.per, { digits: 1, suffix: "x" })} />
                <MetricRow label="PBR" value={formatNumber(data.pbr, { digits: 2, suffix: "x" })} />
                <MetricRow label="PSR" value={formatNumber(data.psr, { digits: 2, suffix: "x" })} />
                <MetricRow label="EV/EBITDA" value={formatNumber(data.ev_ebitda, { digits: 1, suffix: "x" })} />
                <MetricRow label="PEG" value={formatNumber(data.peg_ratio, { digits: 2 })} />
                <MetricRow label="EPS" value={data.eps !== null ? `${data.currency === "JPY" ? "¥" : "$"}${data.eps?.toFixed(2)}` : "—"} />
              </div>

              {/* Profitability */}
              <div className="bg-slate-900 rounded-xl p-4">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">収益性・成長性</h4>
                <MetricRow label="ROE" value={formatNumber(data.roe, { digits: 1, suffix: "%" })} />
                <MetricRow label="ROA" value={formatNumber(data.roa, { digits: 1, suffix: "%" })} />
                <MetricRow label="営業利益率" value={formatNumber(data.operating_margin, { digits: 1, suffix: "%" })} />
                <MetricRow label="純利益率" value={formatNumber(data.net_margin, { digits: 1, suffix: "%" })} />
                <MetricRow label="売上高成長率" value={formatNumber(data.revenue_growth, { digits: 1, suffix: "%" })} />
                <MetricRow label="利益成長率" value={formatNumber(data.earnings_growth, { digits: 1, suffix: "%" })} />
              </div>

              {/* Financial health */}
              <div className="bg-slate-900 rounded-xl p-4">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">財務健全性・株主還元</h4>
                <MetricRow label={market === "JP" ? "自己資本比率" : "D/E Ratio"} value={market === "JP" ? formatNumber(data.equity_ratio, { digits: 1, suffix: "%" }) : formatNumber(data.debt_to_equity, { digits: 2 })} />
                <MetricRow label="流動比率" value={formatNumber(data.current_ratio, { digits: 2 })} />
                <MetricRow label="配当利回り" value={formatNumber(data.dividend_yield, { digits: 2, suffix: "%" })} />
                <MetricRow label="配当性向" value={formatNumber(data.payout_ratio, { digits: 1, suffix: "%" })} />
                <MetricRow label="目標株価" value={data.target_price ? formatPrice(data.target_price, data.currency) : "—"} />
                <MetricRow label="推奨" value={data.recommendation || "—"} />
              </div>
            </div>

            {/* Company info */}
            <div className="bg-slate-900 rounded-xl p-4 flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">会社概要</h4>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-5">
                  {data.description || "説明なし"}
                </p>
              </div>
              <div className="flex-shrink-0 space-y-2 text-sm">
                {data.employees && (
                  <div className="flex items-center gap-2 text-slate-400">
                    <Users className="w-3 h-3" />
                    <span className="text-xs">{data.employees.toLocaleString()} 名</span>
                  </div>
                )}
                {data.country && (
                  <div className="flex items-center gap-2 text-slate-400">
                    <Globe className="w-3 h-3" />
                    <span className="text-xs">{data.country}</span>
                  </div>
                )}
                {data.website && (
                  <a
                    href={data.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                  >
                    <ExternalLink className="w-3 h-3" />
                    公式サイト
                  </a>
                )}
              </div>
            </div>

            {/* AI Analysis */}
            <AIAnalysisPanel symbol={symbol} market={market} />
          </div>
        ) : null}
      </div>
    </div>
  );
}
