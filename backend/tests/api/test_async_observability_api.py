from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event
from tests.api._vuln_case_test_helper import seed_case


def test_async_dispatch_and_ticket_sync_write_queue_events() -> None:
    engine = get_engine()
    seed_case(engine, 9301, state='confirmed', tenant_id='t1', risk_score=8.8, owner='alice')

    client = TestClient(app)
    dispatch = client.post(
        '/api/v1/notifications/dispatch',
        json={
            'tenant_id': 't1',
            'provider': 'webhook',
            'min_risk_score': 7.0,
            'mode': 'async',
        },
    )
    assert dispatch.status_code == 200
    dispatch_job_id = dispatch.json()['job_id']
    assert dispatch_job_id

    ticket = client.post(
        '/api/v1/tickets/sync',
        json={
            'tenant_id': 't1',
            'provider': 'mock_jira',
            'case_ids': [9301],
            'mode': 'async',
        },
    )
    assert ticket.status_code == 200
    ticket_job_id = ticket.json()['job_id']
    assert ticket_job_id

    with Session(engine) as session:
        notification_event = session.execute(
            select(Event)
            .where(Event.event_type == 'notification_async_queued')
            .where(Event.reference_id == dispatch_job_id)
        ).scalar_one_or_none()
        ticket_event = session.execute(
            select(Event)
            .where(Event.event_type == 'ticket_sync_async_queued')
            .where(Event.reference_id == ticket_job_id)
        ).scalar_one_or_none()

    assert notification_event is not None
    assert ticket_event is not None


def test_metrics_exposes_async_queue_counters() -> None:
    client = TestClient(app)
    client.post(
        '/api/v1/notifications/dispatch',
        json={
            'tenant_id': 't1',
            'provider': 'webhook',
            'min_risk_score': 7.0,
            'mode': 'async',
        },
    )
    client.post(
        '/api/v1/tickets/sync',
        json={
            'tenant_id': 't1',
            'provider': 'mock_jira',
            'case_ids': [1],
            'mode': 'async',
        },
    )

    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'lightscan_notification_async_queued_total' in response.text
    assert 'lightscan_ticket_sync_async_queued_total' in response.text
