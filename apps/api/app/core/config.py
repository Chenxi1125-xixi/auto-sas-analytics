from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Auto SAS Analytics API"
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)

    database_url: str = Field(default="sqlite:///./apps/api/local.db")
    storage_root: str = Field(default="storage")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
