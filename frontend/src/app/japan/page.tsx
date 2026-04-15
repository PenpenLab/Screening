"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { FilterPanel } from "@/components/ScreeningPanel/FilterPanel";
import { StockTable } from "@/components/StockTable/StockTable";
import { StockDetailModal } from "@/components/StockDetail/StockDetailModal";
import { api } from "@/lib/api";
import type { ScreeningFilter, StockMetrics } from "@/types/stock";
import { Flag } from "lucide-react";

const DEFAULT_FILTERS: ScreeningFilter = {
  sort_by: "market_cap",
  sort_order: "desc",
  limit: 50,
};

export default function JapanPage() {
  const [stocks, setStocks] = useState<StockMetrics[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [hasRun, setHasRun] = useState(false);

  const mutation = useMutation({
    mutationFn: (filters: ScreeningFilter) => api.screenJapan(filters),
    onSuccess: (data) => {
      setStocks(data);
      setHasRun(true);
    },
  });

  return (
    <div>
      <div className="flex items-center gap-2 mb-6">
        <span className="text-2xl">🇯🇵</span>
        <div>
          <h1 className="text-2xl font-bold text-white">日本株スクリーニング</h1>
          <p className="text-sm text-slate-400">東証上場銘柄 · PER/PBR/ROE/配当利回りで絞り込み</p>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-5">
        {/* Filter panel */}
        <div className="lg:w-72 flex-shrink-0">
          <FilterPanel
            market="JP"
            onFilter={(f) => mutation.mutate(f)}
            loading={mutation.isPending}
          />
        </div>

        {/* Results */}
        <div className="flex-1 min-w-0">
          {mutation.isError && (
            <div className="bg-red-950 border border-red-800 rounded-xl p-4 text-red-300 text-sm mb-4">
              エラーが発生しました: {(mutation.error as Error).message}
            </div>
          )}

          {!hasRun && !mutation.isPending && (
            <div className="flex flex-col items-center justify-center py-20 text-slate-500">
              <Flag className="w-12 h-12 mb-3 opacity-30" />
              <p>スクリーニング条件を設定して「実行」を押してください</p>
              <button
                className="mt-4 text-sm text-blue-400 hover:text-blue-300"
                onClick={() => mutation.mutate(DEFAULT_FILTERS)}
              >
                デフォルト条件で実行 →
              </button>
            </div>
          )}

          {mutation.isPending && (
            <div className="text-center py-20 text-slate-400">
              <div className="inline-block w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-3" />
              <p>スクリーニング中...</p>
            </div>
          )}

          {hasRun && !mutation.isPending && (
            <>
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-slate-400">{stocks.length} 銘柄</span>
              </div>
              <StockTable
                stocks={stocks}
                market="JP"
                onSelect={setSelected}
              />
            </>
          )}
        </div>
      </div>

      {selected && (
        <StockDetailModal
          symbol={selected}
          market="JP"
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  );
}
