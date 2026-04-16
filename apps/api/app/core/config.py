from functools import lru_cache
from pathlib import Path
import os


class Settings:
    app_name: str = "Auto SAS Analytics API"
    debug: bool = True
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./storage/app.db")
    storage_root: str = os.getenv(
        "STORAGE_ROOT",
        str(Path(__file__).resolve().parents[2] / "storage")
    )
    frontend_origin: str = os.getenv(
        "FRONTEND_ORIGIN",
        "http://127.0.0.1:3000"
    )
    sas_command: str = os.getenv("SAS_COMMAND", "sas")
    sas_run_timeout_seconds: int = int(os.getenv("SAS_RUN_TIMEOUT_SECONDS", "60"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
    