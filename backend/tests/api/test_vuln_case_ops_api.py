from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event
from tests.api._vuln_case_test_helper import seed_case


def test_vuln_case_list_supports_filters_and_sorting() -> None:
    engine = get_engine()
    now = datetime.now(timezone.utc)
    seed_case(engine, 201, state='confirmed', owner='alice', risk_score=8.8, sla_due_at=now + timedelta(days=1), tenant_id='t1')
    seed_case(engine, 202, state='in_progress', owner='bob', risk_score=5.0, sla_due_at=now + timedelta(days=5), tenant_id='t1')
    seed_case(engine, 203, state='confirmed', owner='alice', risk_score=9.3, sla_due_at=now - timedelta(days=1), tenant_id='t1')

    client = TestClient(app)
    response = client.get(
        '/api/v1/vuln-cases',
        params={
            'tenant_id': 't1',
            'state': 'confirmed',
            'owner': 'alice',
            'overdue_only': True,
            'sort_by': 'risk_score',
            'sort_order': 'desc',
            'page': 1,
            'page_size': 20,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 1
    assert body['items'][0]['case_id'] == 203


def test_vuln_case_assign_updates_owner_and_sla_and_writes_event() -> None:
    engine = get_engine()
    seed_case(engine, 301, state='confirmed', tenant_id='t1')

    client = TestClient(app)
    response = client.patch(
        '/api/v1/vuln-cases/301/assign',
        params={'tenant_id': 't1'},
        json={
            'owner': 'sec-oncall',
            'sla_due_at': '2026-07-01T00:00:00Z',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['case_id'] == 301
    assert body['owner'] == 'sec-oncall'
    assert body['sla_due_at'] == '2026-07-01T00:00:00Z'

    with Session(engine) as session:
        event = session.execute(
            select(Event)
            .where(Event.event_type == 'vuln_case_assigned')
            .where(Event.reference_id == '301')
            .order_by(Event.event_id.desc())
        ).scalar_one_or_none()
        assert event is not None


def test_vuln_case_assign_rejects_cross_tenant() -> None:
    engine = get_engine()
    seed_case(engine, 302, state='confirmed', tenant_id='t1')

    client = TestClient(app)
    response = client.patch(
        '/api/v1/vuln-cases/302/assign',
        params={'tenant_id': 't2'},
        json={
            'owner': 'sec-oncall',
            'sla_due_at': '2026-07-01T00:00:00Z',
        },
    )
    assert response.status_code == 404
