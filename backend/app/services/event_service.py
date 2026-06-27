import json

from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app.models.event import Event


def _dump_payload(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False)


def log_event(conn: Connection, tenant_id: str, event_type: str, reference_id: str, payload: dict) -> None:
    conn.execute(
        Event.__table__.insert().values(
            tenant_id=tenant_id,
            event_type=event_type,
            reference_id=reference_id,
            payload_json=_dump_payload(payload),
        )
    )


def log_event_with_session(
    session: Session,
    tenant_id: str,
    event_type: str,
    reference_id: str,
    payload: dict,
) -> None:
    session.execute(
        Event.__table__.insert().values(
            tenant_id=tenant_id,
            event_type=event_type,
            reference_id=reference_id,
            payload_json=_dump_payload(payload),
        )
    )
