from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.services.event_service import log_event_with_session


def test_job_status_returns_queued_for_async_notification_job() -> None:
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
    job_id = dispatch.json()['job_id']
    assert job_id

    status_resp = client.get('/api/v1/jobs/status', params={'tenant_id': 't1', 'job_id': job_id})
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body['job_id'] == job_id
    assert body['status'] == 'queued'
    assert body['job_type'] == 'notification'


def test_job_status_returns_success_after_completion_event() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='notification_async_finished',
            reference_id='job-success-1',
            payload={'processed': 1},
        )
        session.commit()

    client = TestClient(app)
    status_resp = client.get('/api/v1/jobs/status', params={'tenant_id': 't1', 'job_id': 'job-success-1'})
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body['status'] == 'success'
    assert body['job_type'] == 'notification'


def test_job_status_returns_failed_after_failure_event() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='ticket_sync_async_failed',
            reference_id='job-failed-1',
            payload={'error': 'boom'},
        )
        session.commit()

    client = TestClient(app)
    status_resp = client.get('/api/v1/jobs/status', params={'tenant_id': 't1', 'job_id': 'job-failed-1'})
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body['status'] == 'failed'
    assert body['job_type'] == 'ticket_sync'


def test_job_status_returns_error_and_retry_metadata_for_failed_job() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='notification_async_failed',
            reference_id='job-failed-meta-1',
            payload={
                'error': 'provider timeout',
                'retry_count': 2,
                'last_retry_at': '2026-06-24T06:00:00Z',
            },
        )
        session.commit()

    client = TestClient(app)
    status_resp = client.get('/api/v1/jobs/status', params={'tenant_id': 't1', 'job_id': 'job-failed-meta-1'})
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body['status'] == 'failed'
    assert body['job_type'] == 'notification'
    assert body['last_error'] == 'provider timeout'
    assert body['retry_count'] == 2
    assert body['last_retry_at'] == '2026-06-24T06:00:00Z'
