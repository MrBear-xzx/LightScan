from fastapi.testclient import TestClient

from app.main import app


def test_auth_register_and_login() -> None:
    client = TestClient(app)

    # register
    reg = client.post('/api/v1/auth/register', json={
        'tenant_id': 't1', 'username': 'testuser', 'password': 'test1234', 'role': 'admin',
    })
    assert reg.status_code == 201
    assert reg.json()['username'] == 'testuser'

    # duplicate registration
    dup = client.post('/api/v1/auth/register', json={
        'tenant_id': 't1', 'username': 'testuser', 'password': 'test1234',
    })
    assert dup.status_code == 409

    # login
    login = client.post('/api/v1/auth/login', json={
        'tenant_id': 't1', 'username': 'testuser', 'password': 'test1234',
    })
    assert login.status_code == 200
    body = login.json()
    assert 'access_token' in body
    assert body['role'] == 'admin'

    # me
    me = client.get('/api/v1/auth/me', headers={'Authorization': 'Bearer ' + body['access_token']})
    assert me.status_code == 200
    assert me.json()['username'] == 'testuser'


def test_auth_invalid_credentials() -> None:
    client = TestClient(app)
    resp = client.post('/api/v1/auth/login', json={
        'tenant_id': 't1', 'username': 'nonexistent', 'password': 'wrong',
    })
    assert resp.status_code == 401
