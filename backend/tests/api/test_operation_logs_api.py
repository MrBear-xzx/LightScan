from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event


def test_operation_logs_empty() -> None:
    client = TestClient(app)
    resp = client.get('/api/v1/ops/logs', params={'tenant_id': 't_empty'})
    assert resp.status_code == 200
    body = resp.json()
    assert body['total'] == 0
    assert body['items'] == []


def test_operation_logs_returns_events() -> None:
    engine = get_engine()
    with Session(engine) as session:
        session.query(Event).delete()
        session.add_all([
            Event(tenant_id='t1', event_type='test_event',
                  reference_id='ref1', payload_json='{"key":"val"}'),
            Event(tenant_id='t1', event_type='test_event',
                  reference_id='ref2', payload_json='{"key":"val2"}'),
        ])
        session.commit()

    client = TestClient(app)
    resp = client.get('/api/v1/ops/logs', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    body = resp.json()
    assert body['total'] >= 2
    assert len(body['items']) >= 2


def test_operation_logs_supports_event_type_filter() -> None:
    client = TestClient(app)
    resp = client.get('/api/v1/ops/logs', params={
        'tenant_id': 't1',
        'event_type': 'nonexistent_type',
    })
    assert resp.status_code == 200
    assert resp.json()['total'] == 0
