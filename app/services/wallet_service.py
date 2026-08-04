from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.wallet import Wallet
from app.schemas.wallets import OperationType, WalletOperationRequest


class WalletService:
    """Сервис для работы с кошельками (бизнес-логика)"""

    @staticmethod
    async def get_wallet(session: AsyncSession, wallet_id: UUID) -> Wallet:
        """
        Получение кошелька по ID.
        Без блокировки, только для чтения.
        """

        # Получаем кошелёк по UUID
        result = await session.execute(select(Wallet).where(Wallet.id == wallet_id))
        wallet = result.scalar_one_or_none()

        # Если кошелёк не найден
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
        """

        # Открываем транзакцию.
        # Все изменения будут либо полностью зафиксированы, либо отменены.
        async with session.begin():
            # Блокируем строку кошелька до завершения транзакции.
            # Это гарантирует последовательное изменение баланса при одновременных запросах к одному кошельку.
            result = await session.execute(
                select(Wallet)
                .where(Wallet.id == wallet_id)
                .with_for_update()
            )
            wallet = result.scalar_one_or_none()

            # Если кошелёк не найден
            if not wallet:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Wallet not found"
                )

            # Пополнение баланса
            if data.operation_type == OperationType.DEPOSIT:
                wallet.balance += data.amount

            # Списание средств
            elif data.operation_type == OperationType.WITHDRAW:

                # Проверяем достаточно ли средств на кошельке
                if wallet.balance < data.amount:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Not enough money"
                    )
                wallet.balance -= data.amount

        # После успешного завершения транзакции SQLAlchemy выполнит COMMIT,
        # а PostgreSQL автоматически снимет блокировку строки.

        return wallet
