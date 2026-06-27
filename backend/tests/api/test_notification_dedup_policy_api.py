from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event
from tests.api._vuln_case_test_helper import seed_case


def test_notification_dispatch_supports_dedup_by_risk_level_policy() -> None:
    engine = get_engine()
    seed_case(engine, 9401, state='confirmed', tenant_id='t1', risk_score=9.2, owner='alice')
    seed_case(engine, 9402, state='confirmed', tenant_id='t1', risk_score=6.2, owner='bob')

    client = TestClient(app)
    policy = {
        'high': 60,
        'medium': 0,
        'low': 0,
    }
    first = client.post(
        '/api/v1/notifications/dispatch',
        json={
            'tenant_id': 't1',
            'min_risk_score': 5.0,
            'dedup_policy_by_risk': policy,
        },
    )
    assert first.status_code == 200
    assert first.json()['dispatched'] == 2

    second = client.post(
        '/api/v1/notifications/dispatch',
        json={
            'tenant_id': 't1',
            'min_risk_score': 5.0,
            'dedup_policy_by_risk': policy,
        },
    )
    assert second.status_code == 200
    second_body = second.json()
    assert second_body['dispatched'] == 1
    assert second_body['suppressed'] == 1

    with Session(engine) as session:
        high_suppressed = session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.event_type == 'notification_suppressed')
            .where(Event.reference_id == '9401')
        ).scalar_one()
        medium_suppressed = session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.event_type == 'notification_suppressed')
            .where(Event.reference_id == '9402')
        ).scalar_one()
    assert high_suppressed == 1
    assert medium_suppressed == 0
