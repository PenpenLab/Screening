import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(
  value: number | null,
  options?: {
    digits?: number;
    suffix?: string;
    prefix?: string;
    abs?: boolean;
  }
): string {
  if (value === null || value === undefined) return "—";
  const v = options?.abs ? Math.abs(value) : value;
  const formatted = v.toFixed(options?.digits ?? 1);
  return `${options?.prefix ?? ""}${formatted}${options?.suffix ?? ""}`;
}

export function formatMarketCap(cap: number | null, currency: string): string {
  if (cap === null) return "—";
  const sym = currency === "JPY" ? "¥" : "$";
  if (Math.abs(cap) >= 1e12) return `${sym}${(cap / 1e12).toFixed(2)}T`;
  if (Math.abs(cap) >= 1e9) return `${sym}${(cap / 1e9).toFixed(1)}B`;
  if (Math.abs(cap) >= 1e6) return `${sym}${(cap / 1e6).toFixed(0)}M`;
  return `${sym}${cap.toLocaleString()}`;
}

export function formatPrice(price: number | null, currency: string): string {
  if (price === null) return "—";
  const sym = currency === "JPY" ? "¥" : "$";
  if (currency === "JPY") return `${sym}${price.toLocaleString("ja-JP")}`;
  return `${sym}${price.toFixed(2)}`;
}

export function colorClass(value: number | null, positive: "green" | "red" = "green"): string {
  if (value === null) return "text-gray-400";
  if (value > 0) return positive === "green" ? "text-green-500" : "text-red-500";
  if (value < 0) return positive === "green" ? "text-red-500" : "text-green-500";
  return "text-gray-400";
}
