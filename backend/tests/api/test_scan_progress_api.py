from fastapi.testclient import TestClient

from app.main import app


def test_scan_progress_returns_empty_for_unknown_batch() -> None:
    client = TestClient(app)
    response = client.get(
        '/api/v1/scan/progress',
        params={'tenant_id': 't1', 'batch_id': 'batch-nonexistent'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 0
    assert body['tasks'] == []


def test_scan_progress_returns_empty_without_filters() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/scan/progress', params={'tenant_id': 't1'})
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 0


def test_scan_progress_supports_task_ids() -> None:
    client = TestClient(app)
    response = client.get(
        '/api/v1/scan/progress',
        params={'tenant_id': 't1', 'task_ids': '999999,999998'},
    )
    assert response.status_code == 200
    body = response.json()
    # task_ids > current max => empty since tasks don't exist
    assert body['total'] <= 2
