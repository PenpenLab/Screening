export type Market = "JP" | "US";

export interface StockMetrics {
  symbol: string;
  name: string;
  market: Market;
  price: number | null;
  change_pct: number | null;
  market_cap: number | null;
  volume: number | null;
  per: number | null;
  pbr: number | null;
  psr: number | null;
  ev_ebitda: number | null;
  roe: number | null;
  roa: number | null;
  operating_margin: number | null;
  net_margin: number | null;
  revenue_growth: number | null;
  earnings_growth: number | null;
  eps_growth: number | null;
  equity_ratio: number | null;
  debt_to_equity: number | null;
  current_ratio: number | null;
  dividend_yield: number | null;
  payout_ratio: number | null;
  fcf_yield: number | null;
  peg_ratio: number | null;
  bps: number | null;
  eps: number | null;
  sector: string | null;
  industry: string | null;
  currency: string;
}

export interface StockDetail extends StockMetrics {
  description: string | null;
  website: string | null;
  employees: number | null;
  country: string | null;
  exchange: string | null;
  week52_high: number | null;
  week52_low: number | null;
  target_price: number | null;
  recommendation: string | null;
}

export interface PriceHistory {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ScreeningFilter {
  per_min?: number;
  per_max?: number;
  pbr_min?: number;
  pbr_max?: number;
  roe_min?: number;
  roa_min?: number;
  operating_margin_min?: number;
  revenue_growth_min?: number;
  earnings_growth_min?: number;
  dividend_yield_min?: number;
  equity_ratio_min?: number;
  debt_to_equity_max?: number;
  market_cap_min?: number;
  market_cap_max?: number;
  sectors?: string[];
  sort_by?: string;
  sort_order?: "asc" | "desc";
  limit?: number;
}

export interface AIAnalysisResponse {
  symbol: string;
  summary: string;
  strengths: string[];
  risks: string[];
  verdict: "bullish" | "neutral" | "bearish";
  verdict_reason: string;
  disclaimer: string;
}

export interface SearchResult {
  symbol: string;
  name: string;
  exchange: string;
  type: string;
}
