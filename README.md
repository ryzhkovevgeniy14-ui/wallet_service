# Wallet Service

Асинхронный REST API сервис для управления балансами кошельков.

## Технологии

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — ORM (асинхронный)
- **asyncpg** — драйвер PostgreSQL
- **Alembic** — миграции БД
- **pytest** — тестирование
- **Docker** — контейнеризация

## Запуск через Docker Compose

```bash
docker-compose up -d
```

## Сервисы:

- **API:** http://localhost:8000

- **Swagger документация:** http://localhost:8000/docs

- **База данных:** localhost:5432

## API Эндпоинты
### Получение баланса кошелька
```http
GET /api/v1/wallets/{wallet_id}
```
### Ответ (200 OK):

```json
{
  "balance": 100
}
```

### Изменение баланса
```http
POST /api/v1/wallets/{wallet_id}/operation
Content-Type: application/json
```
```json
{
  "operation_type": "DEPOSIT",
  "amount": 1000
}
```
### Ответ (200 OK):
```json
{
  "balance": 1100
}
```
### Параметры:

 - **operation_type:** **DEPOSIT** (пополнение) или **WITHDRAW** (списание)

- **amount:** целое число, больше 0

### Коды ответа:

- **200** — **успешно**

- **400** — **недостаточно средств или неверные параметры**

- **404** — **кошелёк не найден**

## Примеры запросов (curl)
```bash
# Получить баланс
curl http://localhost:8000/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000

# Пополнить кошелёк
curl -X POST http://localhost:8000/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type": "DEPOSIT", "amount": 500}'

# Снять деньги
curl -X POST http://localhost:8000/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type": "WITHDRAW", "amount": 300}'
```

## Тестирование
```bash
# Получение кошелька
pytest tests/test_wallet.py::test_wallet_exists -v

# Кошелёк не найден
pytest tests/test_wallet.py::test_wallet_not_found -v

# Пополнение
pytest tests/test_wallet.py::test_deposit -v

# Снятие
pytest tests/test_wallet.py::test_withdraw -v

# Снятие больше баланса
pytest tests/test_wallet.py::test_withdraw_too_much -v

# Конкурентность
pytest tests/test_wallet.py::test_concurrent_withdraw -v
```
## Структура проекта
```txt
text
├── app/
│   ├── core/          # конфигурация
│   ├── db/            # БД: сессии, зависимости
│   ├── models/        # SQLAlchemy модели
│   ├── routers/       # эндпоинты
│   ├── schemas/       # Pydantic схемы
│   ├── services/      # бизнес-логика
│   └── main.py        # точка входа
├── migrations/        # alembic миграции
├── tests/             # тесты
├── docker-compose.yaml
├── Dockerfile
└── requirements.txt
```

