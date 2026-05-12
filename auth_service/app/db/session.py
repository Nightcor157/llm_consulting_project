from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

if not settings.database_url:
    sqlite_path = Path(settings.sqlite_path)
    parent = sqlite_path.parent
    if str(parent) not in ("", "."):
        parent.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(settings.sqlalchemy_database_url, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
