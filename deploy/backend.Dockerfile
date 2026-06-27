FROM python:3.12-slim

WORKDIR /app
COPY backend/pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy alembic psycopg[binary] redis celery pydantic
COPY backend /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
