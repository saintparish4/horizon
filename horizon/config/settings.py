"""Application settings, loaded from environment / .env."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Core ---
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    # --- Database ---
    # asyncpg driver; the sync form is accepted and rewritten in database.py.
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/horizon"
    )
    db_echo: bool = Field(default=False)
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)

    # --- Embeddings ---
    openai_api_key: str | None = Field(default=None)
    embedding_model: str = Field(default="text-embedding-3-small")
    embedding_dimensions: int = Field(default=1536)
    embedding_batch_size: int = Field(default=100)

    # --- Auth ---
    # Server-side pepper mixed into API key hashes. MUST be set in production.
    api_key_pepper: str = Field(default="dev-only-insecure-pepper")

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")


@lru_cache
def get_settings() -> Settings:
    return Settings()
