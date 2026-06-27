from fastapi.testclient import TestClient

from app.main import app


def test_notification_dispatch_async_returns_job_id() -> None:
    client = TestClient(app)
    response = client.post(
        '/api/v1/notifications/dispatch',
        json={
            'tenant_id': 't1',
            'provider': 'webhook',
            'min_risk_score': 7.0,
            'mode': 'async',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['mode'] == 'async'
    assert body['job_id']


def test_ticket_sync_async_returns_job_id() -> None:
    client = TestClient(app)
    response = client.post(
        '/api/v1/tickets/sync',
        json={
            'tenant_id': 't1',
            'provider': 'mock_jira',
            'case_ids': [1, 2],
            'mode': 'async',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['mode'] == 'async'
    assert body['job_id']
