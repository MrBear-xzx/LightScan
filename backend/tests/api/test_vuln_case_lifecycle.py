from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event
from tests.api._vuln_case_test_helper import seed_case


def test_vuln_case_state_transition() -> None:
    seed_case(get_engine(), 123, 'confirmed', tenant_id='t1')
    client = TestClient(app)
    response = client.patch('/api/v1/vuln-cases/123/state', params={'tenant_id': 't1'}, json={'new_state': 'in_progress'})
    assert response.status_code == 200
    assert response.json()['state'] == 'in_progress'


def test_vuln_case_state_transition_writes_event() -> None:
    engine = get_engine()
    seed_case(engine, 456, 'confirmed', tenant_id='t1')
    client = TestClient(app)
    response = client.patch('/api/v1/vuln-cases/456/state', params={'tenant_id': 't1'}, json={'new_state': 'in_progress'})
    assert response.status_code == 200

    with Session(engine) as session:
        event = session.execute(
            select(Event)
            .where(Event.event_type == 'vuln_case_state_changed')
            .where(Event.reference_id == '456')
            .order_by(Event.event_id.desc())
        ).scalar_one_or_none()
        assert event is not None


def test_vuln_case_invalid_transition_rejected() -> None:
    seed_case(get_engine(), 123, 'confirmed', tenant_id='t1')
    client = TestClient(app)
    response = client.patch('/api/v1/vuln-cases/123/state', params={'tenant_id': 't1'}, json={'new_state': 'fixed'})
    assert response.status_code == 400


def test_vuln_case_not_found() -> None:
    client = TestClient(app)
    response = client.patch('/api/v1/vuln-cases/999999/state', params={'tenant_id': 't1'}, json={'new_state': 'in_progress'})
    assert response.status_code == 404


def test_vuln_case_state_transition_rejects_cross_tenant() -> None:
    seed_case(get_engine(), 789, 'confirmed', tenant_id='t1')
    client = TestClient(app)
    response = client.patch('/api/v1/vuln-cases/789/state', params={'tenant_id': 't2'}, json={'new_state': 'in_progress'})
    assert response.status_code == 404
