# Итоговый проект: двухсервисная система LLM-консультаций

Проект реализует два независимых сервиса:

- **Auth Service** — FastAPI-сервис регистрации, логина и выпуска JWT.
- **Bot Service** — Telegram-бот на aiogram, который принимает JWT, валидирует его без обращения к базе Auth Service и отправляет LLM-запросы через Celery/RabbitMQ.

JWT создаётся только в Auth Service. Bot Service не хранит пользователей, не регистрирует их и не обращается к базе Auth Service. В Bot Service токен только проверяется по `JWT_SECRET` и `JWT_ALG`.

## Архитектура

```text
Пользователь -> Swagger Auth Service -> регистрация / логин -> JWT
Пользователь -> Telegram Bot -> /token <JWT> -> Redis token:<tg_user_id>
Пользователь -> Telegram Bot -> текстовый вопрос
Telegram Bot -> проверка JWT -> Celery task -> RabbitMQ
Celery Worker -> OpenRouter -> Telegram Bot API -> ответ пользователю
Redis -> хранение JWT и backend результатов Celery
```

## Структура

```text
auth_service/
  app/
    api/
    core/
    db/
    repositories/
    schemas/
    usecases/
  tests/
bot_service/
  app/
    bot/
    core/
    infra/
    services/
    tasks/
  tests/
docker-compose.yml
```

## Переменные окружения

В проекте уже есть учебные `.env`-файлы. Для реального запуска Telegram-бота нужно заполнить:

```env
# bot_service/.env
TELEGRAM_BOT_TOKEN=<token from BotFather>
OPENROUTER_API_KEY=<openrouter api key>
```

Секрет JWT должен совпадать в обоих сервисах:

```env
JWT_SECRET=change_me_super_secret
JWT_ALG=HS256
```

Для демонстрации по ТЗ регистрируйте email в формате `surname@email.com`.

## Запуск через Docker Compose

```bash
docker compose up --build
```

После запуска доступны:

- Auth Swagger: http://localhost:8000/docs
- Bot Service health: http://localhost:8001/health
- RabbitMQ Management: http://localhost:15672  
  Логин: `guest`, пароль: `guest`

## Сценарий проверки

1. Откройте Swagger Auth Service: http://localhost:8000/docs
2. Выполните `POST /auth/register`:

```json
{
  "email": "surname@email.com",
  "password": "password123"
}
```

3. Выполните `POST /auth/login` через form-data Swagger:
   - `username`: `surname@email.com`
   - `password`: `password123`
4. Скопируйте `access_token`.
5. В Telegram отправьте боту:

```text
/token <access_token>
```

6. После подтверждения отправьте обычный вопрос. Бот ответит, что запрос принят, а Celery worker обработает задачу через RabbitMQ и отправит итоговый ответ.

## Локальный запуск без Docker

Для каждого сервиса используется `uv`.

### Auth Service

```bash
cd auth_service
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Bot Service API

```bash
cd bot_service
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Bot polling

```bash
cd bot_service
uv run python -m app.bot.dispatcher
```

### Celery worker

```bash
cd bot_service
uv run celery -A app.infra.celery_app:celery_app worker --loglevel=info
```

Для локального запуска RabbitMQ и Redis можно поднять только инфраструктуру:

```bash
docker compose up rabbitmq redis
```

## Тесты

Тесты не требуют реального Telegram, Redis, RabbitMQ или OpenRouter.

### Auth Service

```bash
cd auth_service
uv sync
uv run pytest -q
```

Проверяется:

- хеширование и проверка паролей;
- создание и декодирование JWT с `sub`, `role`, `iat`, `exp`;
- полный HTTP-сценарий `register -> login -> me`;
- негативные сценарии: дубль email, неверный пароль, отсутствие/невалидность токена.

### Bot Service

```bash
cd bot_service
uv sync
uv run pytest -q
```

Проверяется:

- JWT-валидация Bot Service;
- `/token <jwt>` с сохранением в fakeredis;
- отказ без токена;
- публикация задачи через мок `llm_request.delay` при валидном токене;
- OpenRouter-клиент через `respx` без реального интернета.

## Скриншоты для сдачи

По ТЗ к работе нужно приложить скриншоты:

1. Swagger Auth Service: успешная регистрация.
2. Swagger Auth Service: успешный логин и получение JWT.
3. Swagger Auth Service: успешный `/auth/me` с Bearer-токеном.
4. Telegram: команда `/token <jwt>` и подтверждение сохранения токена.
5. Telegram: обычный вопрос и ответ LLM.
6. RabbitMQ Management: очередь Celery, messages/consumers/connections.
7. Успешный запуск тестов Auth Service.
8. Успешный запуск тестов Bot Service.

Сохранённые демонстрационные скриншоты:

- [Swagger register](docs/screenshots/01-swagger-register.jpg)
- [Swagger login + JWT](docs/screenshots/02-swagger-login-token.jpg)
- [Telegram LLM answer](docs/screenshots/03-telegram-llm-answer.jpg)
- [RabbitMQ overview](docs/screenshots/04-rabbitmq-overview.jpg)

## Важные архитектурные решения

- `Auth Service` хранит пароль только как bcrypt-хеш.
- `Auth Service` выпускает JWT с `sub`, `role`, `iat`, `exp`.
- `Bot Service` не создаёт JWT и не знает пароли пользователей.
- JWT пользователя привязывается к Telegram `user_id` через Redis-ключ `token:<tg_user_id>`.
- LLM-запросы не выполняются в Telegram-хэндлере: хэндлер только публикует Celery-задачу.
- RabbitMQ реально используется как Celery broker.
- Redis реально используется как Celery backend и как хранилище JWT для Telegram-пользователей.
