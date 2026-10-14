from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = "Dream Deluxe API"
    mongo_uri: str
    mongo_database: str = "dreamsDeluxe"
    jwt_secret_key: str
    jwt_access_token_minutes: int = 30
    default_currency: str = "RON"
    smtp_sender_email: str | None = None
    smtp_password: str | None = None
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
