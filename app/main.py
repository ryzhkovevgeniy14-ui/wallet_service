from fastapi import FastAPI

from app.routers.wallets import router as wallets_router


app = FastAPI(
    title="Wallet service",
    description="Сервис для управления балансами кошельков",
    version="1.0.0",
)

# Подключаем роутеры с префиксом /api/v1/wallets
app.include_router(wallets_router, prefix="/api/v1/wallets")