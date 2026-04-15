"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "ホーム" },
  { href: "/japan", label: "日本株" },
  { href: "/us", label: "米国株" },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
      <div className="container mx-auto px-4 max-w-7xl h-14 flex items-center gap-6">
        <Link href="/" className="flex items-center gap-2 font-bold text-lg text-white">
          <TrendingUp className="w-5 h-5 text-blue-400" />
          <span>StockScreener</span>
        </Link>
        <nav className="flex gap-1 ml-4">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                pathname === item.href
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:text-white hover:bg-slate-800"
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto text-xs text-slate-500">
          Powered by Claude AI
        </div>
      </div>
    </header>
  );
}
