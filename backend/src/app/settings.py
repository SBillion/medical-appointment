"""Application settings loaded from environment (12-factor app)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/backend_exercise"
    cors_origins: list[str] = ["http://localhost:5173"]

    # Test-specific: the base Postgres server URL (without a database name).
    # The conftest creates `test_database_name` on this server at startup.
    test_database_url: str = (
        "postgresql+asyncpg://app:app@localhost:5432/backend_exercise"
    )
    test_database_name: str = "backend_exercise_test"


settings = Settings()
