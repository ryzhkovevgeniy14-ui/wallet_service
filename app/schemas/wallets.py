from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from enum import Enum


class OperationType(str, Enum):
    """
    Перечисление типов операций с кошельком.

    DEPOSIT — пополнение баланса
    WITHDRAW — списание средств
    """
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletOperationRequest(BaseModel):
    """
    Модель запроса для выполнения операции с кошельком.
    Используется в POST-запросах.

    Содержит тип операции и сумму.
    """
    operation_type: Annotated[
        OperationType,
        Field(
            description="Тип операции: DEPOSIT или WITHDRAW"
        )
    ]
    amount: Annotated[
        int,
        Field(
            gt=0,
            description="Сумма операции, должна быть больше 0"
        )
    ]


class WalletResponse(BaseModel):
    """
    Модель ответа с данными кошелька.
    Используется в GET-запросах.

    Возвращает текущий баланс.
    """
    balance: Annotated[
        int,
        Field(
            description="Баланс кошелька"
        )
    ]

    model_config = ConfigDict(from_attributes=True)