FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY . .
RUN mkdir -p /app/data

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
