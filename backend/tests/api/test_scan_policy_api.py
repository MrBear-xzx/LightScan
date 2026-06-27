from fastapi.testclient import TestClient

from app.main import app


def test_scan_policy_list_empty() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/scan/policies', params={'tenant_id': 't1'})
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 0


def test_scan_policy_crud() -> None:
    client = TestClient(app)
    payload = {
        'tenant_id': 't1',
        'name': 'quick-scan',
        'description': '??????',
        'plugins': [
            {'plugin_id': 'nuclei_json', 'enabled': True, 'config': {'timeout': 30}},
        ],
        'extra_config': {'max_concurrency': 5},
    }
    put = client.put('/api/v1/scan/policies', json=payload)
    assert put.status_code == 200
    body = put.json()
    assert body['name'] == 'quick-scan'
    assert body['plugins'][0]['plugin_id'] == 'nuclei_json'

    get = client.get('/api/v1/scan/policies/quick-scan', params={'tenant_id': 't1'})
    assert get.status_code == 200
    assert get.json()['description'] == '??????'

    delete = client.delete('/api/v1/scan/policies/quick-scan', params={'tenant_id': 't1'})
    assert delete.status_code == 204

    get_after = client.get('/api/v1/scan/policies/quick-scan', params={'tenant_id': 't1'})
    assert get_after.status_code == 404


def test_scan_policy_delete_returns_404_for_nonexistent() -> None:
    client = TestClient(app)
    response = client.delete('/api/v1/scan/policies/nonexistent', params={'tenant_id': 't1'})
    assert response.status_code == 404
