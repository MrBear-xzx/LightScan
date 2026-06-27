from fastapi.testclient import TestClient

from app.main import app


def test_plugins_list_supports_status_filter() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/plugins', params={'status': 'enabled'})
    assert response.status_code == 200
    body = response.json()
    assert body['total'] >= 1
    assert all(item['status'] == 'enabled' for item in body['items'])


def test_plugins_list_supports_disabled_filter() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/plugins', params={'status': 'disabled'})
    assert response.status_code == 200
    body = response.json()
    assert body['total'] >= 1
    assert all(item['status'] == 'disabled' for item in body['items'])


def test_plugins_health_counts_only_enabled_plugins() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/plugins/health')
    assert response.status_code == 200
    body = response.json()
    assert body['total'] >= 1
    assert body['healthy'] == body['total']
    for item in body['items']:
        assert item['status'] == 'healthy'
