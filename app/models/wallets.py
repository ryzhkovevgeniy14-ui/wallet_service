from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Wallet(Base):
    """
    Таблица кошельков.

    Используется для хранения баланса.
    """
    __tablename__ = "wallets"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)