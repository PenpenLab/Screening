import Link from "next/link";
import { TrendingUp, Search, BarChart3, Bot } from "lucide-react";

const FEATURES = [
  {
    icon: Search,
    title: "高度なスクリーニング",
    desc: "PER・PBR・ROE・配当利回りなど日本株・米国株それぞれに最適な指標でフィルタリング",
  },
  {
    icon: BarChart3,
    title: "インタラクティブチャート",
    desc: "株価履歴を1ヶ月〜5年で表示。終値・出来高をビジュアルで確認",
  },
  {
    icon: Bot,
    title: "Claude AI 分析",
    desc: "Anthropic Claude による財務データ分析。強み・リスク・投資判断を日本語で提供",
  },
  {
    icon: TrendingUp,
    title: "詳細な財務指標",
    desc: "バリュエーション・収益性・成長性・財務健全性・株主還元の全指標を一覧で確認",
  },
];

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero */}
      <section className="text-center py-16">
        <div className="inline-flex items-center gap-2 bg-blue-950 border border-blue-800 rounded-full px-4 py-1.5 text-blue-300 text-sm mb-6">
          <Bot className="w-4 h-4" />
          Claude AI 搭載
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
          プロ仕様の
          <span className="text-blue-400"> 株式スクリーニング</span>
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-8">
          日本株・米国株を網羅。AI による深い財務分析で、投資判断をサポートします。
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/japan"
            className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
          >
            日本株をスクリーニング
          </Link>
          <Link
            href="/us"
            className="bg-slate-800 hover:bg-slate-700 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
          >
            米国株をスクリーニング
          </Link>
        </div>
      </section>

      {/* Features */}
      <section>
        <h2 className="text-2xl font-bold text-white text-center mb-8">主な機能</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-colors"
              >
                <div className="bg-blue-950 w-10 h-10 rounded-lg flex items-center justify-center mb-3">
                  <Icon className="w-5 h-5 text-blue-400" />
                </div>
                <h3 className="font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-sm text-slate-400">{feature.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Metrics overview */}
      <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-lg font-bold text-white mb-4">対応指標</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
          <div>
            <h4 className="text-blue-400 font-medium mb-2">バリュエーション</h4>
            <ul className="space-y-1 text-slate-400">
              <li>PER / P/E Ratio</li>
              <li>PBR / P/B Ratio</li>
              <li>PSR / P/S Ratio</li>
              <li>EV/EBITDA</li>
              <li>PEGレシオ</li>
            </ul>
          </div>
          <div>
            <h4 className="text-green-400 font-medium mb-2">収益性</h4>
            <ul className="space-y-1 text-slate-400">
              <li>ROE / ROA</li>
              <li>営業利益率</li>
              <li>純利益率</li>
              <li>FCF Yield</li>
            </ul>
          </div>
          <div>
            <h4 className="text-yellow-400 font-medium mb-2">成長性</h4>
            <ul className="space-y-1 text-slate-400">
              <li>売上高成長率 (YoY)</li>
              <li>利益成長率 (YoY)</li>
              <li>EPS成長率</li>
            </ul>
          </div>
          <div>
            <h4 className="text-purple-400 font-medium mb-2">財務健全性</h4>
            <ul className="space-y-1 text-slate-400">
              <li>自己資本比率 (JP)</li>
              <li>D/E Ratio</li>
              <li>流動比率</li>
              <li>配当利回り</li>
              <li>配当性向</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}
