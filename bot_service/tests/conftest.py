from collections.abc import AsyncGenerator

import fakeredis.aioredis
import pytest

from app.bot import handlers


@pytest.fixture
async def fake_redis(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[fakeredis.aioredis.FakeRedis, None]:
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(handlers, "get_redis", lambda: redis)
    try:
        yield redis
    finally:
        await redis.aclose()
