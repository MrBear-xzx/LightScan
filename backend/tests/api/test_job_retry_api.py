from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event
from app.services.event_service import log_event_with_session


def test_job_retry_requeues_failed_notification_job() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='notification_async_failed',
            reference_id='job-retry-1',
            payload={
                'provider': 'webhook',
                'min_risk_score': 7.0,
                'dedup_window_minutes': 30,
            },
        )
        session.commit()

    client = TestClient(app)
    response = client.post(
        '/api/v1/jobs/retry',
        json={
            'tenant_id': 't1',
            'job_id': 'job-retry-1',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'queued'
    assert body['source_job_id'] == 'job-retry-1'
    assert body['new_job_id']
    assert body['job_type'] == 'notification'


def test_job_retry_rejects_when_exceed_max_retry_count() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='notification_async_failed',
            reference_id='job-retry-max',
            payload={
                'provider': 'webhook',
                'min_risk_score': 7.0,
                'retry_count': 3,
            },
        )
        session.commit()

    client = TestClient(app)
    response = client.post(
        '/api/v1/jobs/retry',
        json={'tenant_id': 't1', 'job_id': 'job-retry-max'},
    )
    assert response.status_code == 409


def test_job_retry_rejects_when_in_cooldown_window() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='notification_async_failed',
            reference_id='job-retry-cooldown',
            payload={
                'provider': 'webhook',
                'min_risk_score': 7.0,
                'last_retry_at': '2030-01-01T00:00:00Z',
                'retry_count': 1,
            },
        )
        session.commit()

    client = TestClient(app)
    response = client.post(
        '/api/v1/jobs/retry',
        json={'tenant_id': 't1', 'job_id': 'job-retry-cooldown'},
    )
    assert response.status_code == 409


def test_job_retry_policy_can_be_upserted_and_queried() -> None:
    client = TestClient(app)
    put = client.put(
        '/api/v1/jobs/retry-policy',
        json={
            'tenant_id': 't1',
            'max_retry_count': 5,
            'retry_cooldown_seconds': 120,
        },
    )
    assert put.status_code == 200
    put_body = put.json()
    assert put_body['max_retry_count'] == 5
    assert put_body['retry_cooldown_seconds'] == 120

    get_resp = client.get('/api/v1/jobs/retry-policy', params={'tenant_id': 't1'})
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body['max_retry_count'] == 5
    assert body['retry_cooldown_seconds'] == 120


def test_job_retry_uses_tenant_policy_over_default_guardrails() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='notification_async_failed',
            reference_id='job-retry-policy-1',
            payload={
                'provider': 'webhook',
                'min_risk_score': 7.0,
                'retry_count': 2,
                'last_retry_at': '2030-01-01T00:00:00Z',
            },
        )
        session.commit()

    client = TestClient(app)
    set_policy = client.put(
        '/api/v1/jobs/retry-policy',
        json={
            'tenant_id': 't1',
            'max_retry_count': 10,
            'retry_cooldown_seconds': 0,
        },
    )
    assert set_policy.status_code == 200

    response = client.post(
        '/api/v1/jobs/retry',
        json={'tenant_id': 't1', 'job_id': 'job-retry-policy-1'},
    )
    assert response.status_code == 200


def test_job_retry_policy_upsert_writes_audit_event() -> None:
    client = TestClient(app)
    response = client.put(
        '/api/v1/jobs/retry-policy',
        json={
            'tenant_id': 't1',
            'max_retry_count': 6,
            'retry_cooldown_seconds': 180,
        },
    )
    assert response.status_code == 200

    engine = get_engine()
    with Session(engine) as session:
        event = session.execute(
            select(Event)
            .where(Event.tenant_id == 't1')
            .where(Event.event_type == 'job_retry_policy_updated')
            .order_by(Event.event_id.desc())
            .limit(1)
        ).scalar_one_or_none()
        assert event is not None
        assert event.reference_id == 't1'
        assert '"max_retry_count": 6' in event.payload_json
        assert '"retry_cooldown_seconds": 180' in event.payload_json
