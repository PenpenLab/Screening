# Stock Screening App | 株式スクリーニングアプリ

日本株・米国株スクリーニング Webアプリ。財務指標フィルタリング + Claude AI による銘柄分析。

## 技術スタック

| Layer      | Technology |
|------------|------------|
| Frontend   | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| Backend    | Python FastAPI, yfinance, pandas |
| AI         | Anthropic Claude API (claude-sonnet-4-6) |
| Data       | Yahoo Finance (yfinance) |

## セットアップ

### 1. バックエンド

```bash
cd backend
cp .env.example .env
# .env に ANTHROPIC_API_KEY を設定

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

### 2. フロントエンド

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

## 主な機能

### 日本株スクリーニング
- PER / PBR フィルター
- ROE / ROA / 営業利益率
- 自己資本比率 (日本株特有)
- 配当利回り / 売上高成長率 / 時価総額フィルター

### 米国株スクリーニング
- P/E / P/B / PEG Ratio
- EPS成長率 / 売上高成長率
- D/E Ratio / 配当利回り / 営業利益率

### AI分析 (Claude)
- 財務データの総合分析
- 強み・リスクの列挙
- 投資判断 (強気/中立/弱気)
- 日本語レポート生成

## API エンドポイント

```
GET  /api/stocks/search?q=&market=JP|US   銘柄検索
GET  /api/stocks/{symbol}?market=         銘柄詳細
GET  /api/stocks/{symbol}/history         株価履歴
POST /api/screening/japan                 日本株スクリーニング
POST /api/screening/us                    米国株スクリーニング
POST /api/analysis/ai                     AI分析
GET  /health                              ヘルスチェック
```

## 免責事項

本アプリは情報提供目的のみです。投資判断は自己責任で行ってください。
