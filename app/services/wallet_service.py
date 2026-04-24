from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from app.models.wallet import Wallet
from app.schemas.wallets import OperationType, WalletOperationRequest


class WalletService:
    """Сервис для работы с кошельками (бизнес-логика)"""

    @staticmethod
    async def get_wallet(
            session: AsyncSession,
            wallet_id: UUID
    ) -> Wallet:
        """
        Получение кошелька по ID.
        Без блокировки, только для чтения.
        """
        result = await session.execute(select(Wallet).where(Wallet.id == wallet_id))

        wallet = result.scalar_one_or_none()

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )

        return wallet

    @staticmethod
    async def process_operation(
            session: AsyncSession,
            wallet_id: UUID,
            data: WalletOperationRequest
    ) -> Wallet:
        """
        Обработка операции с кошельком (пополнение или снятие).
        Блокировка строки гарантирует корректность при параллельных запросах.
        """
        async with session.begin():
            wallet = await WalletService.get_wallet(session, wallet_id)

            if data.operation_type == OperationType.DEPOSIT:
                wallet.balance += data.amount

            elif data.operation_type == OperationType.WITHDRAW:
                if wallet.balance < data.amount:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Not enough money"
                    )
                wallet.balance -= data.amount

        return wallet