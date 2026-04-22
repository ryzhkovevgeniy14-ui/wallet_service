from fastapi import APIRouter, status
from uuid import UUID

from app.schemas.wallets import WalletOperationRequest, WalletResponse


router = APIRouter()


@router.get("/{wallet_id}", response_model=WalletResponse, status_code=status.HTTP_200_OK)
async def get_wallet(wallet_id: UUID):
    """
    Получение текущего баланса кошелька
    """
    ...


@router.post("/{wallet_id}/operation", response_model=WalletResponse, status_code=status.HTTP_200_OK)
async def wallet_operation(wallet_id: UUID, data: WalletOperationRequest):
    """
    Изменение баланса кошелька.

    Поддерживает операции:
    - DEPOSIT — увеличение баланса
    - WITHDRAW — уменьшение баланса
    """
    ...