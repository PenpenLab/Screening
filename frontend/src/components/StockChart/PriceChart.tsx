"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { api } from "@/lib/api";
import type { Market } from "@/types/stock";

interface Props {
  symbol: string;
  market: Market;
  currency: string;
}

const PERIODS = [
  { value: "1mo", label: "1M" },
  { value: "3mo", label: "3M" },
  { value: "6mo", label: "6M" },
  { value: "1y", label: "1Y" },
  { value: "2y", label: "2Y" },
  { value: "5y", label: "5Y" },
];

export function PriceChart({ symbol, market, currency }: Props) {
  const [period, setPeriod] = useState("1y");

  const { data, isLoading } = useQuery({
    queryKey: ["history", market, symbol, period],
    queryFn: () => api.getHistory(symbol, market, period),
  });

  const priceSymbol = currency === "JPY" ? "¥" : "$";
  const firstClose = data?.[0]?.close ?? 0;
  const lastClose = data?.[data.length - 1]?.close ?? 0;
  const isPositive = lastClose >= firstClose;

  if (isLoading) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500">
        チャート読み込み中...
      </div>
    );
  }

  return (
    <div>
      <div className="flex gap-1 mb-3">
        {PERIODS.map((p) => (
          <button
            key={p.value}
            onClick={() => setPeriod(p.value)}
            className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
              period === p.value
                ? "bg-blue-600 text-white"
                : "text-slate-400 hover:text-white hover:bg-slate-700"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={isPositive ? "#22c55e" : "#ef4444"} stopOpacity={0.3} />
              <stop offset="95%" stopColor={isPositive ? "#22c55e" : "#ef4444"} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="date"
            tickFormatter={(v: string) => v.slice(5)}
            tick={{ fontSize: 11, fill: "#64748b" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(v: number) => `${priceSymbol}${v.toLocaleString()}`}
            tick={{ fontSize: 11, fill: "#64748b" }}
            axisLine={false}
            tickLine={false}
            width={70}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid #334155",
              borderRadius: "8px",
              fontSize: 12,
            }}
            formatter={(value: number) => [`${priceSymbol}${value.toFixed(2)}`, "終値"]}
            labelStyle={{ color: "#94a3b8" }}
          />
          <Area
            type="monotone"
            dataKey="close"
            stroke={isPositive ? "#22c55e" : "#ef4444"}
            strokeWidth={2}
            fill="url(#colorClose)"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
