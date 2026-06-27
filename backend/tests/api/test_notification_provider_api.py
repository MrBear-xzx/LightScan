from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event
from tests.api._vuln_case_test_helper import seed_case


def test_notification_dispatch_supports_feishu_provider() -> None:
    engine = get_engine()
    seed_case(engine, 8101, state='confirmed', tenant_id='t1', risk_score=8.8, owner='alice')

    client = TestClient(app)
    response = client.post(
        '/api/v1/notifications/dispatch',
        json={
            'tenant_id': 't1',
            'min_risk_score': 7.0,
            'provider': 'feishu',
            'webhook_url': 'http://127.0.0.1:9/feishu',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['provider'] == 'feishu'

    with Session(engine) as session:
        event = session.execute(
            select(Event)
            .where(Event.event_type == 'notification_feishu_failed')
            .where(Event.reference_id == '8101')
        ).scalar_one_or_none()
        assert event is not None
