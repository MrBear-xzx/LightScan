from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event
from tests.api._vuln_case_test_helper import seed_case


def test_vuln_report_export_csv() -> None:
    engine = get_engine()
    seed_case(engine, 2101, state='confirmed', tenant_id='t1', risk_score=9.4, owner='alice')
    seed_case(engine, 2102, state='fixed', tenant_id='t1', risk_score=4.2, owner='bob')

    client = TestClient(app)
    response = client.get('/api/v1/reports/vuln/export.csv', params={'tenant_id': 't1'})
    assert response.status_code == 200
    assert 'text/csv' in response.headers.get('content-type', '')
    assert 'case_id,tenant_id,state,risk_score,owner' in response.text
    assert '2101,t1,confirmed,9.4,alice' in response.text


def test_notification_dispatch_writes_events() -> None:
    engine = get_engine()
    seed_case(engine, 2201, state='confirmed', tenant_id='t1', risk_score=8.3, owner='alice')
    seed_case(engine, 2202, state='fixed', tenant_id='t1', risk_score=9.2, owner='bob')

    client = TestClient(app)
    response = client.post('/api/v1/notifications/dispatch', json={'tenant_id': 't1', 'min_risk_score': 7.0})
    assert response.status_code == 200
    body = response.json()
    assert body['tenant_id'] == 't1'
    assert body['dispatched'] == 1

    with Session(engine) as session:
        count = session.execute(
            select(Event)
            .where(Event.event_type == 'notification_dispatched')
            .where(Event.reference_id == '2201')
        ).scalar_one_or_none()
        assert count is not None
