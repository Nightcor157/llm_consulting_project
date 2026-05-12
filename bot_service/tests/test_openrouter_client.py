import pytest
import respx
from httpx import Response

from app.core.config import settings
from app.services.openrouter_client import call_openrouter


@pytest.mark.asyncio
@respx.mock
async def test_call_openrouter_returns_content() -> None:
    route = respx.post(f"{settings.openrouter_base_url}/chat/completions").mock(
        return_value=Response(
            200,
            json={"choices": [{"message": {"content": "Тестовый ответ LLM"}}]},
        )
    )

    answer = await call_openrouter("Тестовый запрос")

    assert answer == "Тестовый ответ LLM"
    assert route.called
