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
Перед запуском создайте файл `.env`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
POSTGRES_DB=wallet_service_db

DATABASE_URL=postgresql+asyncpg://postgres:admin@localhost:5432/wallet_service_db
```
Запуск приложения:
```bash
docker compose up --build
```
Если PostgreSQL уже запускался ранее и необходимо пересоздать базу:
```bash
docker compose down -v
docker compose up --build
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

## Конкурентность

Для корректной обработки параллельных операций над одним кошельком используется блокировка строки PostgreSQL:

```python
SELECT ... FOR UPDATE
```

В SQLAlchemy используется:

```python
.with_for_update()
```

Это предотвращает состояние гонки при одновременном изменении баланса несколькими запросами.

Транзакция гарантирует, что операции изменения баланса выполняются последовательно.

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

Запуск всех тестов:

```bash
docker compose exec app pytest tests/test_wallet.py -v
```

Проверяемые сценарии:

- получение существующего кошелька;
- получение несуществующего кошелька;
- пополнение баланса;
- списание средств;
- попытка списания большей суммы;
- конкурентное выполнение двух операций;
- стресс-тест: 10 параллельных списаний.

## Структура проекта

```txt
├── app/
│   ├── core/              # конфигурация приложения
│   ├── db/                # подключение к БД, сессии, зависимости
│   ├── models/            # SQLAlchemy модели
│   ├── routers/           # API endpoints
│   ├── schemas/           # Pydantic схемы запросов и ответов
│   ├── services/          # бизнес-логика
│   └── main.py            # точка входа приложения
├── migrations/            # Alembic миграции
├── tests/                 # автоматические тесты
├── alembic.ini            # конфигурация Alembic
├── pytest.ini             # конфигурация pytest
├── docker-compose.yaml    # запуск приложения и PostgreSQL
├── Dockerfile             # сборка контейнера приложения
├── requirements.txt       # зависимости Python
└── README.md

