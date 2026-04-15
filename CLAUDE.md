# Stock Screening App - Claude Code Guide

## Project Overview
日本株・米国株スクリーニングWebアプリ。リアルタイム株価データ、財務指標分析、AI（Claude API）による銘柄分析を提供する。

## Architecture
```
Screening/
├── frontend/          # Next.js 14 (App Router) + TypeScript + Tailwind CSS
├── backend/           # Python FastAPI + yfinance + Anthropic SDK
├── CLAUDE.md          # このファイル
└── README.md
```

## Tech Stack
| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| Backend    | Python 3.11+, FastAPI, yfinance, pandas |
| AI         | Anthropic Claude API (claude-sonnet-4-6) |
| Data       | Yahoo Finance (yfinance)            |

## Development Commands

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
npm run build
npm run lint
```

## Key Features

### Japanese Stock Screening (日本株)
- 対象: JPX上場銘柄 (証券コード 4桁)
- 主要指標: PER, PBR, ROE, ROA, 配当利回り, 自己資本比率
- 売上高/営業利益成長率, 時価総額フィルター
- セクター分類 (東証33業種)

### US Stock Screening (米国株)
- 対象: NYSE/NASDAQ上場銘柄
- 主要指標: P/E, P/B, EPS Growth, Free Cash Flow Yield, Dividend Yield
- Revenue Growth, Operating Margin, Debt/Equity Ratio
- Sector classification (GICS)

### AI Analysis (Claude)
- 銘柄の財務分析レポート生成
- 強み・リスク・投資判断の要約
- 日本語/英語対応
- prompt caching で API コスト最適化

## Environment Variables
```
# backend/.env
ANTHROPIC_API_KEY=your_key_here
ALLOWED_ORIGINS=http://localhost:3000
```

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/stocks/search | 銘柄検索 |
| GET | /api/stocks/{symbol} | 銘柄詳細・財務データ |
| GET | /api/stocks/{symbol}/history | 株価履歴 |
| POST | /api/screening/japan | 日本株スクリーニング |
| POST | /api/screening/us | 米国株スクリーニング |
| POST | /api/analysis/ai | AI分析レポート生成 |

## Coding Conventions
- Python: type hints必須, pydantic models for request/response
- TypeScript: strict mode, no `any`
- Components: functional components + hooks only
- API calls: React Query (TanStack Query) for caching/loading states
