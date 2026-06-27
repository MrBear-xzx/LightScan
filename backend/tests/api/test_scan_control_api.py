from fastapi.testclient import TestClient

from app.main import app


def test_scan_cancel_returns_404_for_nonexistent_task() -> None:
    client = TestClient(app)
    response = client.post('/api/v1/scan/999999/cancel', params={'tenant_id': 't1'})
    assert response.status_code == 404


def test_scan_cancel_succeeds_for_pending_task() -> None:
    client = TestClient(app)
    # Create a task first
    create_resp = client.post('/api/v1/scan/batch', json={
        'tenant_id': 't1',
        'batches': [{'targets': ['example.com'], 'policy_id': 'default-external'}],
    })
    assert create_resp.status_code == 200
    task_id = create_resp.json()['tasks'][0]['task_id']

    cancel_resp = client.post(f'/api/v1/scan/{task_id}/cancel', params={'tenant_id': 't1'})
    assert cancel_resp.status_code == 200
    body = cancel_resp.json()
    assert body['status'] == 'cancelled'


def test_scan_cancel_rejects_already_cancelled() -> None:
    client = TestClient(app)
    create_resp = client.post('/api/v1/scan/batch', json={
        'tenant_id': 't1',
        'batches': [{'targets': ['example.com'], 'policy_id': 'default-external'}],
    })
    task_id = create_resp.json()['tasks'][0]['task_id']

    client.post(f'/api/v1/scan/{task_id}/cancel', params={'tenant_id': 't1'})
    second = client.post(f'/api/v1/scan/{task_id}/cancel', params={'tenant_id': 't1'})
    assert second.status_code == 200
    assert 'already finished' in second.json()['message']


def test_scan_timeout_check_returns_count() -> None:
    client = TestClient(app)
    response = client.post('/api/v1/scan/timeout-check', params={
        'tenant_id': 't1',
        'timeout_seconds': 30,
    })
    assert response.status_code == 200
    body = response.json()
    assert 'timed_out_count' in body
    assert 'timed_out_task_ids' in body
