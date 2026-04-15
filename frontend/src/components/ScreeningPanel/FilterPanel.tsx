"use client";

import { useState } from "react";
import { SlidersHorizontal, RotateCcw } from "lucide-react";
import type { Market, ScreeningFilter } from "@/types/stock";

interface Props {
  market: Market;
  onFilter: (f: ScreeningFilter) => void;
  loading: boolean;
}

interface FilterField {
  key: keyof ScreeningFilter;
  label: string;
  suffix?: string;
  min?: number;
  step?: number;
  isRange?: boolean;
  maxKey?: keyof ScreeningFilter;
}

const JP_FIELDS: FilterField[] = [
  { key: "per_min", label: "PER 下限", suffix: "倍", isRange: true, maxKey: "per_max", min: 0, step: 1 },
  { key: "pbr_min", label: "PBR 下限", suffix: "倍", isRange: true, maxKey: "pbr_max", min: 0, step: 0.1 },
  { key: "roe_min", label: "ROE 最低", suffix: "%", min: 0, step: 1 },
  { key: "operating_margin_min", label: "営業利益率 最低", suffix: "%", min: 0, step: 1 },
  { key: "dividend_yield_min", label: "配当利回り 最低", suffix: "%", min: 0, step: 0.5 },
  { key: "equity_ratio_min", label: "自己資本比率 最低", suffix: "%", min: 0, step: 5 },
  { key: "revenue_growth_min", label: "売上高成長率 最低", suffix: "%", step: 1 },
  { key: "market_cap_min", label: "時価総額 下限 (十億)", min: 0, step: 100 },
];

const US_FIELDS: FilterField[] = [
  { key: "per_min", label: "P/E 下限", isRange: true, maxKey: "per_max", min: 0, step: 1 },
  { key: "pbr_min", label: "P/B 下限", isRange: true, maxKey: "pbr_max", min: 0, step: 0.1 },
  { key: "roe_min", label: "ROE 最低 (%)", min: 0, step: 1 },
  { key: "operating_margin_min", label: "営業利益率 最低 (%)", min: 0, step: 1 },
  { key: "dividend_yield_min", label: "配当利回り 最低 (%)", min: 0, step: 0.5 },
  { key: "debt_to_equity_max", label: "D/E レシオ 最大", min: 0, step: 0.5 },
  { key: "revenue_growth_min", label: "売上高成長率 最低 (%)", step: 1 },
  { key: "earnings_growth_min", label: "EPS 成長率 最低 (%)", step: 1 },
  { key: "market_cap_min", label: "時価総額 下限 ($B)", min: 0, step: 10 },
];

const SORT_OPTIONS = [
  { value: "market_cap", label: "時価総額" },
  { value: "per", label: "PER" },
  { value: "pbr", label: "PBR" },
  { value: "roe", label: "ROE" },
  { value: "dividend_yield", label: "配当利回り" },
  { value: "revenue_growth", label: "売上高成長率" },
  { value: "operating_margin", label: "営業利益率" },
];

export function FilterPanel({ market, onFilter, loading }: Props) {
  const fields = market === "JP" ? JP_FIELDS : US_FIELDS;
  const [values, setValues] = useState<Record<string, string>>({});

  const handleChange = (key: string, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }));
  };

  const buildFilter = (): ScreeningFilter => {
    const f: ScreeningFilter = {
      sort_by: values.sort_by || "market_cap",
      sort_order: "desc",
      limit: 50,
    };
    fields.forEach((field) => {
      const v = values[field.key as string];
      if (v && v !== "") {
        (f as Record<string, unknown>)[field.key as string] = parseFloat(v);
      }
      if (field.isRange && field.maxKey) {
        const vMax = values[field.maxKey as string];
        if (vMax && vMax !== "") {
          (f as Record<string, unknown>)[field.maxKey as string] = parseFloat(vMax);
        }
      }
    });
    return f;
  };

  const reset = () => setValues({});

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-slate-200 flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-blue-400" />
          スクリーニング条件
        </h2>
        <button
          onClick={reset}
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1"
        >
          <RotateCcw className="w-3 h-3" /> リセット
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        {fields.map((field) => (
          <div key={field.key as string}>
            <label className="block text-xs text-slate-400 mb-1">{field.label}</label>
            <div className={field.isRange ? "flex gap-1 items-center" : ""}>
              <input
                type="number"
                min={field.min}
                step={field.step}
                placeholder="—"
                value={values[field.key as string] ?? ""}
                onChange={(e) => handleChange(field.key as string, e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-white focus:outline-none focus:border-blue-500"
              />
              {field.isRange && field.maxKey && (
                <>
                  <span className="text-slate-500 text-xs">~</span>
                  <input
                    type="number"
                    min={field.min}
                    step={field.step}
                    placeholder="—"
                    value={values[field.maxKey as string] ?? ""}
                    onChange={(e) => handleChange(field.maxKey as string, e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-white focus:outline-none focus:border-blue-500"
                  />
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mb-4">
        <label className="block text-xs text-slate-400 mb-1">並び替え</label>
        <select
          value={values.sort_by || "market_cap"}
          onChange={(e) => handleChange("sort_by", e.target.value)}
          className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-white focus:outline-none focus:border-blue-500"
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      <button
        onClick={() => onFilter(buildFilter())}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg py-2 text-sm transition-colors"
      >
        {loading ? "スクリーニング中..." : "スクリーニング実行"}
      </button>
    </div>
  );
}
