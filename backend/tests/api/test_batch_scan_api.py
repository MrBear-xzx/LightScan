from fastapi.testclient import TestClient

from app.main import app


def test_batch_scan_creates_tasks() -> None:
    client = TestClient(app)
    response = client.post(
        '/api/v1/scan/batch',
        json={
            'tenant_id': 't1',
            'batches': [
                {'targets': ['example.com'], 'policy_id': 'default-external'},
                {'targets': ['10.0.0.1', '10.0.0.2'], 'policy_id': 'internal-scan'},
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['tenant_id'] == 't1'
    assert body['total'] == 2
    assert body['succeeded'] == 2
    assert body['failed'] == 0
    assert len(body['tasks']) == 2
    assert body['tasks'][0]['task_id'] > 0
    assert body['tasks'][0]['status'] == 'pending'
    assert body['batch_id'].startswith('batch-')


def test_batch_scan_returns_error_on_invalid_target() -> None:
    client = TestClient(app)
    response = client.post(
        '/api/v1/scan/batch',
        json={
            'tenant_id': 't1',
            'batches': [
                {'targets': [], 'policy_id': 'default-external'},
            ],
        },
    )
    # Pydantic ???? targets??? 422
    assert response.status_code == 422


def test_batch_scan_empty_batches_rejected() -> None:
    client = TestClient(app)
    response = client.post(
        '/api/v1/scan/batch',
        json={
            'tenant_id': 't1',
            'batches': [],
        },
    )
    assert response.status_code == 422
