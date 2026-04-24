import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from sqlalchemy import delete

from app.main import app
from app.db.session import async_session_maker
from app.models.wallet import Wallet


@pytest_asyncio.fixture
async def create_wallet():
    """Создаёт тестовый кошелёк с балансом 100. Автоматически удаляет его после теста."""
    wallet_id = uuid4()
    async with async_session_maker() as session:
        session.add(Wallet(id=wallet_id, balance=100))
        await session.commit()
    yield wallet_id
    async with async_session_maker() as session:
        await session.execute(delete(Wallet).where(Wallet.id == wallet_id))
        await session.commit()


@pytest_asyncio.fixture
async def client():
    """HTTP-клиент для тестирования эндпоинтов без реального запуска сервера."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


# ТЕСТ 1: Получение существующего кошелька
@pytest.mark.asyncio
async def test_wallet_exists(create_wallet, client):
    response = await client.get(f"/api/v1/wallets/{create_wallet}")
    assert response.status_code == 200
    assert response.json()["balance"] == 100


# ТЕСТ 2: Получение несуществующего кошелька
@pytest.mark.asyncio
async def test_wallet_not_found(client):
    response = await client.get(f"/api/v1/wallets/{uuid4()}")
    assert response.status_code == 404


# ТЕСТ 3: Пополнение баланса (DEPOSIT)
@pytest.mark.asyncio
async def test_deposit(create_wallet, client):
    response = await client.post(
        f"/api/v1/wallets/{create_wallet}/operation",
        json={"operation_type": "DEPOSIT", "amount": 500}
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 600


# ТЕСТ 4: Снятие денег (WITHDRAW)
@pytest.mark.asyncio
async def test_withdraw(create_wallet, client):
    response = await client.post(
        f"/api/v1/wallets/{create_wallet}/operation",
        json={"operation_type": "WITHDRAW", "amount": 30}
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 70


# ТЕСТ 5: Снятие больше, чем есть на балансе
@pytest.mark.asyncio
async def test_withdraw_too_much(create_wallet, client):
    response = await client.post(
        f"/api/v1/wallets/{create_wallet}/operation",
        json={"operation_type": "WITHDRAW", "amount": 1000}
    )
    assert response.status_code == 400


# ТЕСТ 6: Конкурентность - два параллельных снятия по 60 с баланса 100
@pytest.mark.asyncio
async def test_concurrent_withdraw(create_wallet):
    wallet_id = create_wallet
    transport = ASGITransport(app=app)

    async def withdraw_60():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "WITHDRAW", "amount": 60}
            )

    # Запускаем два запроса параллельно
    responses = await asyncio.gather(withdraw_60(), withdraw_60())
    statuses = [response.status_code for response in responses]

    # Один запрос успешен, второй - ошибка
    assert 200 in statuses
    assert 400 in statuses

    # Проверяем финальный баланс
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        final = await client.get(f"/api/v1/wallets/{wallet_id}")
        assert final.json()["balance"] == 40