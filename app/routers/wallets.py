from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from app.schemas.wallets import WalletOperationRequest, WalletResponse
from app.services.wallet_service import WalletService
from app.db.depends import get_async_db


router = APIRouter()


@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK
)
async def get_wallet(wallet_id: UUID, session: AsyncSession = Depends(get_async_db)):
    """
    Получение текущего баланса кошелька
    """
    wallet = await WalletService.get_wallet(session, wallet_id)
    return wallet


@router.post(
    "/{wallet_id}/operation",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK
)
async def wallet_operation(
    wallet_id: UUID,
    data: WalletOperationRequest,
    session: AsyncSession = Depends(get_async_db)):
    """
    Изменение баланса кошелька.

    Поддерживает операции:
    - DEPOSIT — увеличение баланса
    - WITHDRAW — уменьшение баланса
    """
    wallet = await WalletService.process_operation(session, wallet_id, data)
    return wallet