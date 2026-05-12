from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from jose import jwt

from app.bot.handlers import text_handler, token_handler, token_key
from app.core.config import settings


class FakeMessage:
    def __init__(self, *, user_id: int = 123, chat_id: int = 456, text: str = "") -> None:
        self.from_user = SimpleNamespace(id=user_id)
        self.chat = SimpleNamespace(id=chat_id)
        self.text = text
        self.answers: list[str] = []

    async def answer(self, text: str) -> None:
        self.answers.append(text)


def make_token(subject: str = "42", role: str = "user") -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": subject,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": now + timedelta(minutes=5),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )


@pytest.mark.asyncio
async def test_token_handler_saves_valid_token(fake_redis) -> None:
    token = make_token()
    message = FakeMessage(user_id=123)
    command = SimpleNamespace(args=token)

    await token_handler(message, command)

    saved_token = await fake_redis.get(token_key(123))
    assert saved_token == token
    assert "Токен принят" in message.answers[-1]


@pytest.mark.asyncio
async def test_text_handler_without_token_does_not_call_celery(fake_redis, mocker) -> None:
    delay_mock = mocker.patch("app.bot.handlers.llm_request.delay")
    message = FakeMessage(user_id=123, chat_id=456, text="Привет")

    await text_handler(message)

    delay_mock.assert_not_called()
    assert "Нет сохранённого токена" in message.answers[-1]


@pytest.mark.asyncio
async def test_text_handler_with_valid_token_calls_celery(fake_redis, mocker) -> None:
    token = make_token()
    await fake_redis.set(token_key(123), token)
    delay_mock = mocker.patch("app.bot.handlers.llm_request.delay")
    message = FakeMessage(user_id=123, chat_id=456, text="Расскажи про FastAPI")

    await text_handler(message)

    delay_mock.assert_called_once_with(456, "Расскажи про FastAPI")
    assert "Запрос принят" in message.answers[-1]
