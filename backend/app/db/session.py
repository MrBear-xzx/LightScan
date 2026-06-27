import importlib
import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.db.base import Base

DEFAULT_DATABASE_URL = "sqlite+pysqlite:///./lightscan.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

_MODEL_MODULES = (
    "app.models.asset",
    "app.models.scan_task",
    "app.models.event",
    "app.models.finding",
    "app.models.vuln_case",
    "app.models.policy",
    "app.models.user",
    "app.models.vuln_tag",
    "app.models.vuln_case_tag",
    "app.models.project",
)


def _import_models() -> None:
    for module in _MODEL_MODULES:
        importlib.import_module(module)


def ensure_tables(database_url: str | None = None) -> None:
    """Create all missing tables if they do not exist (idempotent)."""
    _import_models()
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)


def _resolve_database_url(database_url: str | None = None) -> str:
    if database_url:
        return database_url
    return os.getenv("DATABASE_URL", DATABASE_URL)


@lru_cache(maxsize=8)
def _get_cached_engine(url: str) -> Engine:
    return create_engine(url, future=True)


def get_engine(database_url: str | None = None) -> Engine:
    url = _resolve_database_url(database_url)
    return _get_cached_engine(url)


def get_session(database_url: str | None = None) -> Session:
    engine = get_engine(database_url)
    return Session(engine)
