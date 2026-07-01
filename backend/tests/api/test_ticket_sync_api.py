from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event
from tests.api._vuln_case_test_helper import seed_case


def test_ticket_sync_creates_event() -> None:
    engine = get_engine()
    seed_case(engine, 6101, state='confirmed', tenant_id='t1', risk_score=8.2, owner='alice')

    client = TestClient(app)
    response = client.post(
        '/api/v1/tickets/sync',
        json={
            'tenant_id': 't1',
            'provider': 'mock_jira',
            'case_ids': [6101],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['provider'] == 'mock_jira'
    assert body['synced'] == 1

    with Session(engine) as session:
        event = session.execute(
            select(Event)
            .where(Event.event_type == 'ticket_synced')
            .where(Event.reference_id == '6101')
        ).scalar_one_or_none()
        assert event is not None

