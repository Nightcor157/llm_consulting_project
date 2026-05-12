# Проверка проекта

Проверка выполнена в контейнере разработки.

## Auth Service

Команда:

```bash
cd auth_service
uv run pytest -q
uv run ruff check .
```

Результат:

```text
7 passed
All checks passed!
```

## Bot Service

Команда:

```bash
cd bot_service
uv run pytest -q
uv run ruff check .
```

Результат:

```text
6 passed
All checks passed!
```

Unit/integration/mock-тесты не требуют реального Redis, RabbitMQ, Telegram и OpenRouter.
