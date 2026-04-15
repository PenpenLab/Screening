"use client";

import type { Market, StockMetrics } from "@/types/stock";
import { formatNumber, formatMarketCap, formatPrice, colorClass } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface Props {
  stocks: StockMetrics[];
  market: Market;
  onSelect: (symbol: string) => void;
}

const JP_COLS = [
  { key: "name", label: "銘柄" },
  { key: "price", label: "株価" },
  { key: "change_pct", label: "前日比" },
  { key: "market_cap", label: "時価総額" },
  { key: "per", label: "PER" },
  { key: "pbr", label: "PBR" },
  { key: "roe", label: "ROE" },
  { key: "operating_margin", label: "営業利益率" },
  { key: "dividend_yield", label: "配当利回り" },
  { key: "equity_ratio", label: "自己資本比率" },
];

const US_COLS = [
  { key: "name", label: "銘柄" },
  { key: "price", label: "Price" },
  { key: "change_pct", label: "Change" },
  { key: "market_cap", label: "Mkt Cap" },
  { key: "per", label: "P/E" },
  { key: "pbr", label: "P/B" },
  { key: "roe", label: "ROE" },
  { key: "operating_margin", label: "Op. Margin" },
  { key: "dividend_yield", label: "Div. Yield" },
  { key: "revenue_growth", label: "Rev. Growth" },
];

function TrendIcon({ value }: { value: number | null }) {
  if (value === null) return <Minus className="w-3 h-3 text-gray-500 inline" />;
  if (value > 0) return <TrendingUp className="w-3 h-3 text-green-400 inline" />;
  return <TrendingDown className="w-3 h-3 text-red-400 inline" />;
}

function CellValue({ col, stock }: { col: string; stock: StockMetrics }) {
  switch (col) {
    case "name":
      return (
        <div>
          <div className="font-medium text-white">{stock.name}</div>
          <div className="text-xs text-slate-400">{stock.symbol} · {stock.sector || "—"}</div>
        </div>
      );
    case "price":
      return <span className="font-mono">{formatPrice(stock.price, stock.currency)}</span>;
    case "change_pct":
      return (
        <span className={`font-mono flex items-center gap-0.5 ${colorClass(stock.change_pct)}`}>
          <TrendIcon value={stock.change_pct} />
          {stock.change_pct !== null ? `${stock.change_pct > 0 ? "+" : ""}${stock.change_pct.toFixed(2)}%` : "—"}
        </span>
      );
    case "market_cap":
      return <span className="font-mono text-slate-300">{formatMarketCap(stock.market_cap, stock.currency)}</span>;
    case "per":
      return <span className="font-mono">{formatNumber(stock.per, { digits: 1, suffix: "x" })}</span>;
    case "pbr":
      return <span className="font-mono">{formatNumber(stock.pbr, { digits: 2, suffix: "x" })}</span>;
    case "roe":
      return <span className={`font-mono ${stock.roe && stock.roe >= 10 ? "text-green-400" : ""}`}>{formatNumber(stock.roe, { digits: 1, suffix: "%" })}</span>;
    case "operating_margin":
      return <span className={`font-mono ${stock.operating_margin && stock.operating_margin >= 15 ? "text-green-400" : ""}`}>{formatNumber(stock.operating_margin, { digits: 1, suffix: "%" })}</span>;
    case "dividend_yield":
      return <span className={`font-mono ${stock.dividend_yield && stock.dividend_yield >= 2 ? "text-yellow-400" : ""}`}>{formatNumber(stock.dividend_yield, { digits: 2, suffix: "%" })}</span>;
    case "equity_ratio":
      return <span className={`font-mono ${stock.equity_ratio && stock.equity_ratio >= 40 ? "text-green-400" : ""}`}>{formatNumber(stock.equity_ratio, { digits: 1, suffix: "%" })}</span>;
    case "revenue_growth":
      return (
        <span className={`font-mono ${colorClass(stock.revenue_growth)}`}>
          {stock.revenue_growth !== null ? `${stock.revenue_growth > 0 ? "+" : ""}${stock.revenue_growth.toFixed(1)}%` : "—"}
        </span>
      );
    default:
      return <span>—</span>;
  }
}

export function StockTable({ stocks, market, onSelect }: Props) {
  const cols = market === "JP" ? JP_COLS : US_COLS;

  if (stocks.length === 0) {
    return (
      <div className="text-center py-16 text-slate-500">
        条件に合う銘柄が見つかりませんでした。条件を緩めてお試しください。
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-900 border-b border-slate-800">
            {cols.map((col) => (
              <th key={col.key} className="px-4 py-3 text-left text-xs font-medium text-slate-400 whitespace-nowrap">
                {col.label}
              </th>
            ))}
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-400">詳細</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock, i) => (
            <tr
              key={stock.symbol}
              className={`border-b border-slate-800/50 hover:bg-slate-800/40 transition-colors cursor-pointer ${i % 2 === 0 ? "bg-slate-900/30" : ""}`}
              onClick={() => onSelect(stock.symbol)}
            >
              {cols.map((col) => (
                <td key={col.key} className="px-4 py-3 whitespace-nowrap">
                  <CellValue col={col.key} stock={stock} />
                </td>
              ))}
              <td className="px-4 py-3">
                <button
                  onClick={(e) => { e.stopPropagation(); onSelect(stock.symbol); }}
                  className="text-xs text-blue-400 hover:text-blue-300 border border-blue-800 hover:border-blue-600 rounded px-2 py-1 transition-colors"
                >
                  詳細
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
