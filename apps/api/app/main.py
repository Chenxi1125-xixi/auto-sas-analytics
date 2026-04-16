from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.db.init_db import create_tables
from app.db.seed import seed_data
from app.db.session import SessionLocal
from app.routes.health import router as health_router
from app.routes.tasks import router as tasks_router
from app.routes.templates import router as templates_router
from app.routes.uploads import router as uploads_router

settings = get_settings()
storage_root = Path(settings.storage_root)
storage_root.mkdir(parents=True, exist_ok=True)
(storage_root / "uploads").mkdir(parents=True, exist_ok=True)
(storage_root / "results").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/storage", StaticFiles(directory=str(storage_root)), name="storage")

app.include_router(health_router)
app.include_router(templates_router)
app.include_router(uploads_router)
app.include_router(tasks_router)