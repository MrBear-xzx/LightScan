from fastapi.testclient import TestClient

from app.main import app


def test_list_plugins_returns_builtin_plugins() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/plugins')
    assert response.status_code == 200
    body = response.json()
    plugin_ids = {item['plugin_id'] for item in body['items']}
    assert 'http_probe' in plugin_ids
    assert 'nuclei_json' in plugin_ids
    assert 'mockx_json' in plugin_ids


def test_list_plugins_can_filter_by_capability() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/plugins', params={'capability': 'scan'})
    assert response.status_code == 200
    body = response.json()
    assert body['total'] >= 1
    assert all('scan' in item['capabilities'] for item in body['items'])


def test_plugins_health_returns_all_healthy() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/plugins/health')
    assert response.status_code == 200
    body = response.json()
    assert body['total'] >= 1
    assert body['healthy'] == body['total']
    for item in body['items']:
        assert item['status'] == 'healthy'
