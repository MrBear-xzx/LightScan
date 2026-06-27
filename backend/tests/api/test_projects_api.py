from fastapi.testclient import TestClient

from app.main import app


def test_projects_crud() -> None:
    client = TestClient(app)

    # list empty
    resp = client.get('/api/v1/projects', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    assert resp.json()['total'] == 0

    # create
    create = client.post('/api/v1/projects', json={
        'tenant_id': 't1', 'name': 'Test Project', 'description': 'test desc',
    })
    assert create.status_code == 201
    pid = create.json()['project_id']

    # list after create
    resp2 = client.get('/api/v1/projects', params={'tenant_id': 't1'})
    assert resp2.json()['total'] == 1

    # add member
    member = client.post(f'/api/v1/projects/{pid}/members', params={'tenant_id': 't1'}, json={
        'user_id': 1, 'role': 'admin',
    })
    assert member.status_code == 201
    assert member.json()['role'] == 'admin'

    # list members
    members = client.get(f'/api/v1/projects/{pid}/members', params={'tenant_id': 't1'})
    assert members.status_code == 200
    assert len(members.json()) == 1

    # delete
    delete = client.delete(f'/api/v1/projects/{pid}', params={'tenant_id': 't1'})
    assert delete.status_code == 204
