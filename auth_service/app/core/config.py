from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "auth-service"
    env: str = "local"

    jwt_secret: str = "change_me_super_secret"
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 60

    sqlite_path: str = "./auth.db"
    database_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"sqlite+aiosqlite:///{self.sqlite_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
