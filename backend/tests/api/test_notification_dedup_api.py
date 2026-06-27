from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event
from tests.api._vuln_case_test_helper import seed_case


def test_notification_dispatch_suppresses_recent_duplicates() -> None:
    engine = get_engine()
    seed_case(engine, 9101, state='confirmed', tenant_id='t1', risk_score=8.9, owner='alice')

    client = TestClient(app)
    first = client.post(
        '/api/v1/notifications/dispatch',
        json={
            'tenant_id': 't1',
            'min_risk_score': 7.0,
            'dedup_window_minutes': 30,
        },
    )
    assert first.status_code == 200
    first_body = first.json()
    assert first_body['dispatched'] == 1
    assert first_body['suppressed'] == 0

    second = client.post(
        '/api/v1/notifications/dispatch',
        json={
            'tenant_id': 't1',
            'min_risk_score': 7.0,
            'dedup_window_minutes': 30,
        },
    )
    assert second.status_code == 200
    second_body = second.json()
    assert second_body['dispatched'] == 0
    assert second_body['suppressed'] == 1

    with Session(engine) as session:
        dispatched_count = session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.event_type == 'notification_dispatched')
            .where(Event.reference_id == '9101')
        ).scalar_one()
        suppressed_count = session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.event_type == 'notification_suppressed')
            .where(Event.reference_id == '9101')
        ).scalar_one()

    assert dispatched_count == 1
    assert suppressed_count == 1
