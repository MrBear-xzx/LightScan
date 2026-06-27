from fastapi.testclient import TestClient

from app.main import app


def test_backups_empty() -> None:
    client = TestClient(app)
    resp = client.get('/api/v1/ops/backups', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    assert resp.json()['total'] == 0


def test_backup_create_and_list() -> None:
    client = TestClient(app)
    create = client.post('/api/v1/ops/backups', params={'tenant_id': 't1', 'description': 'pre-upgrade backup'})
    assert create.status_code == 201
    body = create.json()
    assert body['status'] == 'completed'
    assert body['backup_id'].startswith('backup-')

    list_resp = client.get('/api/v1/ops/backups', params={'tenant_id': 't1'})
    assert list_resp.status_code == 200
    assert list_resp.json()['total'] >= 1
    assert list_resp.json()['items'][0]['backup_id'] == body['backup_id']
