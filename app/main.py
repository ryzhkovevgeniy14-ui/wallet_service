from fastapi import FastAPI

from app.routers.wallets import router as wallets_router


app = FastAPI(
    title="Wallet service",
    version="1.0.0",
)

app.include_router(wallets_router, prefix="/api/v1/wallets")