from functools import lru_cache
from pathlib import Path


class Settings:
    app_name: str = "Auto SAS Analytics API"
    debug: bool = True
    database_url: str = "sqlite:///./storage/app.db"
    storage_root: str = str(Path(__file__).resolve().parents[2] / "storage")
    frontend_origin: str = "http://127.0.0.1:3000"
    sas_command: str = "sas"
    sas_run_timeout_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
