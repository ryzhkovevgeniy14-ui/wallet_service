from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from app.models.wallets import Wallet
from app.schemas.wallets import OperationType, WalletOperationRequest


class WalletService:
    @staticmethod
    async def get_wallet(
            session: AsyncSession,
            wallet_id: UUID
    ) -> Wallet:
        result = await session.execute(
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .with_for_update()
        )

        wallet = result.scalar_one_or_none()

        if not wallet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

        return wallet

    @staticmethod
    async def process_operation(
            session: AsyncSession,
            wallet_id: UUID,
            data: WalletOperationRequest
    ) -> Wallet:
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

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid operation type"
            )

        await session.commit()
        await session.refresh(wallet)
        return wallet