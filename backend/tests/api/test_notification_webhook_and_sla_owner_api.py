from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.session import get_engine
from app.main import app
from tests.api._vuln_case_test_helper import seed_case


def test_notification_dispatch_returns_webhook_result_fields() -> None:
    engine = get_engine()
    seed_case(engine, 5101, state='confirmed', tenant_id='t1', risk_score=8.5, owner='alice')

    client = TestClient(app)
    response = client.post(
        '/api/v1/notifications/dispatch',
        json={
            'tenant_id': 't1',
            'min_risk_score': 7.0,
            'webhook_url': 'http://127.0.0.1:9/mock-webhook',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['dispatched'] == 1
    assert 'sent' in body
    assert 'failed' in body


def test_notification_dispatch_rejects_tenant_header_mismatch() -> None:
    engine = get_engine()
    seed_case(engine, 5102, state='confirmed', tenant_id='t1', risk_score=8.6, owner='alice')

    client = TestClient(app)
    response = client.post(
        '/api/v1/notifications/dispatch',
        headers={'X-Tenant-ID': 't2'},
        json={
            'tenant_id': 't1',
            'min_risk_score': 7.0,
        },
    )
    assert response.status_code == 403


def test_sla_overview_contains_owner_breakdown() -> None:
    engine = get_engine()
    now = datetime.now(timezone.utc)
    seed_case(engine, 5201, state='confirmed', tenant_id='t1', risk_score=8.0, owner='alice', sla_due_at=now - timedelta(hours=1))
    seed_case(engine, 5202, state='in_progress', tenant_id='t1', risk_score=7.0, owner='alice', sla_due_at=now + timedelta(hours=20))
    seed_case(engine, 5203, state='new', tenant_id='t1', risk_score=6.0, owner=None, sla_due_at=None)

    client = TestClient(app)
    response = client.get('/api/v1/reports/sla/overview', params={'tenant_id': 't1'})
    assert response.status_code == 200

    body = response.json()
    assert 'owner_breakdown' in body
    assert 'alice' in body['owner_breakdown']
    assert body['owner_breakdown']['alice']['total_cases'] == 2
    assert body['owner_breakdown']['alice']['overdue_cases'] == 1
    assert body['owner_breakdown']['unassigned']['total_cases'] == 1
