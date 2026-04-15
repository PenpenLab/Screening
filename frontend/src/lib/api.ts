import type {
  Market,
  StockDetail,
  StockMetrics,
  PriceHistory,
  ScreeningFilter,
  AIAnalysisResponse,
  SearchResult,
} from "@/types/stock";

const BASE = "/api";

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json() as Promise<T>;
}

export const api = {
  searchStocks: (q: string, market: Market): Promise<{ results: SearchResult[] }> =>
    fetchJSON(`${BASE}/stocks/search?q=${encodeURIComponent(q)}&market=${market}`),

  getStock: (symbol: string, market: Market): Promise<StockDetail> =>
    fetchJSON(`${BASE}/stocks/${symbol}?market=${market}`),

  getHistory: (
    symbol: string,
    market: Market,
    period: string
  ): Promise<PriceHistory[]> =>
    fetchJSON(`${BASE}/stocks/${symbol}/history?market=${market}&period=${period}`),

  screenJapan: (filters: ScreeningFilter): Promise<StockMetrics[]> =>
    fetchJSON(`${BASE}/screening/japan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(filters),
    }),

  screenUS: (filters: ScreeningFilter): Promise<StockMetrics[]> =>
    fetchJSON(`${BASE}/screening/us`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(filters),
    }),

  analyzeAI: (
    symbol: string,
    market: Market,
    language: "ja" | "en" = "ja"
  ): Promise<AIAnalysisResponse> =>
    fetchJSON(`${BASE}/analysis/ai`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, market, language }),
    }),
};
