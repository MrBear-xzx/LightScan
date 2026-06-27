import json
import time

from fastapi import Request, Response
from sqlalchemy import create_engine
from starlette.middleware.base import BaseHTTPMiddleware

import os


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)

        # Only log non-GET requests and non-200 responses
        if request.method == 'GET' and response.status_code < 400:
            return response

        tenant_id = request.query_params.get('tenant_id', 'default')

        body_bytes = b''
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            try:
                body_bytes = await request.body()
            except Exception:
                pass

        payload = {
            'method': request.method,
            'path': request.url.path,
            'query_params': dict(request.query_params),
            'status_code': response.status_code,
            'duration_ms': duration_ms,
        }

        if body_bytes:
            try:
                payload['body'] = json.loads(body_bytes)
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload['body'] = body_bytes[:500].decode('utf-8', errors='replace')

        # Write audit event
        from app.models.event import Event
        db_url = os.getenv('DATABASE_URL', 'sqlite+pysqlite:///./lightscan.db')
        engine = create_engine(db_url)
        with engine.begin() as conn:
            conn.execute(
                Event.__table__.insert().values(
                    tenant_id=tenant_id,
                    event_type='api_' + request.method.lower(),
                    reference_id=request.url.path,
                    payload_json=json.dumps(payload, ensure_ascii=False),
                )
            )

        return response
