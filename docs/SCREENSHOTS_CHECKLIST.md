# Чек-лист скриншотов для сдачи

Скриншоты нужно сделать после запуска проекта с реальным Telegram Bot Token и OpenRouter API Key.

1. Swagger Auth Service: `POST /auth/register` с email формата `surname@email.com`.
2. Swagger Auth Service: `POST /auth/login`, получение `access_token`.
3. Swagger Auth Service: `GET /auth/me` с `Authorization: Bearer <token>`.
4. Telegram: команда `/token <jwt>` и подтверждение сохранения токена.
5. Telegram: обычный вопрос и ответ от LLM.
6. RabbitMQ Management: активная Celery-очередь, сообщения, consumers/connections.
7. Терминал: успешные тесты Auth Service (`docs/screenshots/05-auth-service-tests.jpg`).
8. Терминал: успешные тесты Bot Service (`docs/screenshots/06-bot-service-tests.jpg`).
