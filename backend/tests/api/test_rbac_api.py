from fastapi.testclient import TestClient

from app.main import app


def _register_and_login(client, username, role='analyst'):
    client.post('/api/v1/auth/register', json={
        'tenant_id': 't1', 'username': username, 'password': 'pass1234', 'role': role,
    })
    resp = client.post('/api/v1/auth/login', json={
        'tenant_id': 't1', 'username': username, 'password': 'pass1234',
    })
    return resp.json()['access_token']


def test_admin_role_required() -> None:
    client = TestClient(app)
    token = _register_and_login(client, 'test_admin_rbac', 'admin')
    resp = client.get('/api/v1/auth/admin-only', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200


def test_analyst_rejected_for_admin() -> None:
    client = TestClient(app)
    token = _register_and_login(client, 'test_analyst_rbac', 'analyst')
    resp = client.get('/api/v1/auth/admin-only', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 403


def test_viewer_rejected_for_vuln_write() -> None:
    client = TestClient(app)
    token = _register_and_login(client, 'test_viewer_rbac', 'viewer')
    resp = client.get('/api/v1/auth/vuln-write', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 403


def test_analyst_has_vuln_write() -> None:
    client = TestClient(app)
    token = _register_and_login(client, 'test_analyst_vuln', 'analyst')
    resp = client.get('/api/v1/auth/vuln-write', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200


def test_permissions_endpoint() -> None:
    client = TestClient(app)
    token = _register_and_login(client, 'test_admin_perm', 'admin')
    resp = client.get('/api/v1/auth/permissions', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert len(resp.json()['permissions']) > 0
    assert 'admin:all' in resp.json()['permissions']
