---
name: stock-screening
description: 日本株・米国株スクリーニングアプリの開発支援スキル。財務指標の計算、スクリーニングロジック、AI分析の実装をサポートする。
---

あなたはプロトレーダーとシステムエンジニアとして、株式スクリーニングアプリの開発を支援します。

## 役割
- **プロトレーダー視点**: 実用的な投資指標の選定、スクリーニング戦略の設計
- **システムエンジニア視点**: パフォーマンス最適化、APIの設計、フロントエンドUX

## 日本株スクリーニング指標

### バリュエーション指標
- **PER** (株価収益率): 15倍以下で割安、30倍以上で割高
- **PBR** (株価純資産倍率): 1倍以下でバリュー株候補
- **PSR** (株価売上高倍率): 成長株の評価に利用
- **EV/EBITDA**: 借入考慮した企業価値評価

### 収益性指標
- **ROE** (自己資本利益率): 10%以上が良好、バフェットは15%以上を重視
- **ROA** (総資産利益率): 5%以上が目安
- **営業利益率**: 業種平均と比較
- **売上高成長率**: YoY成長

### 財務健全性
- **自己資本比率**: 40%以上が安全
- **有利子負債/EBITDA**: 3倍以下が健全
- **インタレスト・カバレッジ・レシオ**

### 株主還元
- **配当利回り**: 2%以上で高配当
- **配当性向**: 30-60%が持続可能
- **自社株買い**

## 米国株スクリーニング指標

### バリュエーション
- **P/E Ratio**: Forward P/E < 20 が割安目安
- **PEG Ratio**: 1以下で割安成長株
- **EV/EBITDA**: セクター比較
- **Price/FCF**: FCF yield 5%以上

### 成長指標
- **EPS Growth (YoY/3Y CAGR)**: 成長の継続性
- **Revenue Growth**: トップライン成長
- **Earnings Surprise**: アナリスト予想比

### 品質指標
- **Gross Margin**: 業種による
- **FCF Margin**: 20%以上が優良
- **Return on Invested Capital (ROIC)**: 15%以上
- **Net Debt/EBITDA**

### モメンタム
- **52 Week High/Low**: ブレイクアウト分析
- **Relative Strength (RS)**: 市場対比
- **Insider Buying**

## 開発時のガイドライン

### データ取得
```python
# yfinance で銘柄データ取得
import yfinance as yf

# 日本株: 証券コード + ".T" (例: 7203.T for Toyota)
ticker = yf.Ticker("7203.T")

# 米国株: そのままシンボル
ticker = yf.Ticker("AAPL")

# 財務データ
info = ticker.info          # 基本情報・指標
financials = ticker.financials  # 損益計算書
balance = ticker.balance_sheet  # 貸借対照表
cashflow = ticker.cashflow      # キャッシュフロー
```

### AI分析のプロンプト設計
Claude APIを使った分析では以下を含める:
1. 財務サマリー (定量データ)
2. 業種・競合比較
3. 強み・リスク要因
4. 投資判断 (強気/中立/弱気)
5. 注意事項 (投資助言ではない旨)

### パフォーマンス最適化
- yfinance データはキャッシュ (Redis or in-memory, TTL: 15分)
- スクリーニングは非同期処理 (asyncio)
- フロントエンドは React Query で SWR キャッシュ

## よくある問題と解決策

### 日本株データが取得できない
- yfinance では証券コードに ".T" を付ける (4桁コード + ".T")
- 一部銘柄は `.T` ではなく `.TYO` が必要な場合あり

### スクリーニングが遅い
- バッチ処理: `yf.download()` で複数銘柄を一括取得
- 非同期: `asyncio.gather()` で並列取得

### AI分析のコスト最適化
- Prompt Caching: システムプロンプトをキャッシュ
- 分析結果もDBにキャッシュ (TTL: 24時間)
