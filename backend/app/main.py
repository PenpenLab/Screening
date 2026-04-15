from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import stocks, screening, analysis

settings = get_settings()

app = FastAPI(
    title="Stock Screening API",
    description="日本株・米国株スクリーニング & AI分析API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)
app.include_router(screening.router)
app.include_router(analysis.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
