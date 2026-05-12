from typing import Any

import httpx

from app.core.config import settings


class OpenRouterError(RuntimeError):
    pass


class OpenRouterClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.openrouter_api_key
        self.base_url = (base_url if base_url is not None else settings.openrouter_base_url).rstrip("/")
        self.model = model if model is not None else settings.openrouter_model
        self.timeout = timeout

    async def ask(self, prompt: str) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
        except httpx.RequestError as exc:
            raise OpenRouterError(f"OpenRouter network error: {exc}") from exc

        if response.status_code >= 400:
            raise OpenRouterError(
                f"OpenRouter returned {response.status_code}: {response.text[:500]}"
            )

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise OpenRouterError("OpenRouter response has unexpected format") from exc

        if not isinstance(content, str) or not content.strip():
            raise OpenRouterError("OpenRouter returned empty content")
        return content.strip()


async def call_openrouter(prompt: str) -> str:
    return await OpenRouterClient().ask(prompt)
