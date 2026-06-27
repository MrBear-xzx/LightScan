from fastapi.testclient import TestClient
from app.main import app


def test_create_discovery_task_returns_pending() -> None:
    client = TestClient(app)
    payload = {
        'tenant_id': 't1',
        'targets': ['example.com', '198.51.100.10'],
        'policy_id': 'default-external',
    }
    response = client.post('/api/v1/discovery/tasks', json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body['status'] == 'pending'
    assert body['task_type'] == 'discover'
