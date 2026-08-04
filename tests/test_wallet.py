import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from sqlalchemy import delete, select

from app.main import app
from app.db.session import async_session_maker
from app.models.wallet import Wallet


@pytest_asyncio.fixture(scope="function")
async def create_wallet():
    """Создаёт тестовый кошелёк с балансом 1000. Удаляет после теста."""
    wallet_id = uuid4()
    async with async_session_maker() as session:
        async with session.begin():
            session.add(Wallet(id=wallet_id, balance=1000))
    yield wallet_id
    async with async_session_maker() as session:
        async with session.begin():
            await session.execute(delete(Wallet).where(Wallet.id == wallet_id))


# ТЕСТ 1: Получение существующего кошелька
@pytest.mark.asyncio
async def test_wallet_exists(create_wallet):
    wallet_id = create_wallet
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/wallets/{wallet_id}")
        assert response.status_code == 200
        assert response.json()["balance"] == 1000


# ТЕСТ 2: Получение несуществующего кошелька
@pytest.mark.asyncio
async def test_wallet_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/wallets/{uuid4()}")
        assert response.status_code == 404


# ТЕСТ 3: Пополнение баланса (DEPOSIT)
@pytest.mark.asyncio
async def test_deposit(create_wallet):
    wallet_id = create_wallet
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": 500}
        )
        assert response.status_code == 200
        assert response.json()["balance"] == 1500


# ТЕСТ 4: Снятие денег (WITHDRAW)
@pytest.mark.asyncio
async def test_withdraw(create_wallet):
    wallet_id = create_wallet
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "WITHDRAW", "amount": 300}
        )
        assert response.status_code == 200
        assert response.json()["balance"] == 700


# ТЕСТ 5: Снятие больше, чем есть на балансе
@pytest.mark.asyncio
async def test_withdraw_too_much(create_wallet):
    wallet_id = create_wallet
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "WITHDRAW", "amount": 1500}
        )
        assert response.status_code == 400

        # Проверяем, что баланс не изменился
        get_response = await client.get(f"/api/v1/wallets/{wallet_id}")
        assert get_response.json()["balance"] == 1000

# ТЕСТ 6: Конкурентность — два параллельных снятия по 600
@pytest.mark.asyncio
async def test_concurrent_withdraw(create_wallet):
    wallet_id = create_wallet
    transport = ASGITransport(app=app)

    async def withdraw_600():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "WITHDRAW", "amount": 600}
            )

    responses = await asyncio.gather(withdraw_600(), withdraw_600())
    statuses = [r.status_code for r in responses]

    assert 200 in statuses
    assert 400 in statuses

    async with async_session_maker() as session:
        result = await session.execute(
            select(Wallet).where(Wallet.id == wallet_id)
        )
        wallet = result.scalar_one()
        assert wallet.balance == 400


# ТЕСТ 7: Стресс-тест конкурентности — 10 параллельных снятий по 110
@pytest.mark.asyncio
async def test_concurrent_10_withdraws(create_wallet):
    wallet_id = create_wallet
    transport = ASGITransport(app=app)

    async def withdraw_110():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "WITHDRAW", "amount": 110}
            )

    responses = await asyncio.gather(*[withdraw_110() for _ in range(10)])
    statuses = [r.status_code for r in responses]

    assert statuses.count(200) == 9
    assert statuses.count(400) == 1

    async with async_session_maker() as session:
        result = await session.execute(
            select(Wallet).where(Wallet.id == wallet_id)
        )
        wallet = result.scalar_one()
        assert wallet.balance == 10