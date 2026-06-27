import importlib
import os
import time

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from app.db.base import Base

# Ensure Celery eager mode is applied before app modules are imported in tests.
os.environ.setdefault('CELERY_TASK_ALWAYS_EAGER', '1')

# Default to SQLite for local dev; CI overrides via TEST_DATABASE_URL env var
TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')
MODEL_MODULES = (
    'app.models.asset',
    'app.models.scan_task',
    'app.models.event',
    'app.models.finding',
    'app.models.vuln_case',
    'app.models.policy',
    'app.models.user',
)


def _import_model_modules() -> None:
    for module in MODEL_MODULES:
        importlib.import_module(module)


def _wait_for_postgres(url: str, retries: int = 20, interval_seconds: float = 0.5) -> None:
    last_error = None
    for _ in range(retries):
        engine = create_engine(url, future=True)
        try:
            with engine.connect() as conn:
                conn.execute(text('SELECT 1'))
            return
        except Exception as exc:
            last_error = exc
            time.sleep(interval_seconds)
        finally:
            engine.dispose()
    raise RuntimeError(f'PostgreSQL is not ready: {last_error}')


def _truncate_existing_model_tables(engine: Engine) -> None:
    expected_tables = {table.name for table in Base.metadata.sorted_tables}
    existing_tables = set(inspect(engine).get_table_names())
    table_names = sorted(expected_tables & existing_tables)
    if not table_names:
        return

    is_sqlite = 'sqlite' in engine.url.drivername
    with engine.begin() as conn:
        if is_sqlite:
            conn.execute(text("PRAGMA foreign_keys = OFF"))
            for tn in table_names:
                conn.execute(text(f'DELETE FROM "{tn}"'))
            conn.execute(text("PRAGMA foreign_keys = ON"))
        else:
            quoted = ', '.join(f'"{tn}"' for tn in table_names)
            conn.execute(text(f'TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE'))


def pytest_sessionstart(session):
    _wait_for_postgres(TEST_DATABASE_URL)


@pytest.fixture(autouse=True)
def use_test_db(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', TEST_DATABASE_URL)
    monkeypatch.setenv('CELERY_TASK_ALWAYS_EAGER', '1')


@pytest.fixture(autouse=True)
def clean_tables_each_test():
    _import_model_modules()
    engine = create_engine(TEST_DATABASE_URL, future=True)
    Base.metadata.create_all(engine)
    _truncate_existing_model_tables(engine)
    try:
        yield
    finally:
        _truncate_existing_model_tables(engine)
        engine.dispose()


@pytest.fixture()
def db_engine():
    _import_model_modules()
    engine = create_engine(TEST_DATABASE_URL, future=True)
    Base.metadata.create_all(engine)
    _truncate_existing_model_tables(engine)
    try:
        yield engine
    finally:
        _truncate_existing_model_tables(engine)
        engine.dispose()
