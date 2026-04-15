import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import { Header } from "@/components/Layout/Header";

export const metadata: Metadata = {
  title: "Stock Screener | 株式スクリーニング",
  description: "日本株・米国株スクリーニング & AI分析ツール",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <Providers>
          <Header />
          <main className="container mx-auto px-4 py-6 max-w-7xl">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
