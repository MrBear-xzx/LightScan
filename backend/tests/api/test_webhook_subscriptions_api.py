from fastapi.testclient import TestClient

from app.main import app


def test_webhook_subscriptions_crud() -> None:
    client = TestClient(app)

    # list empty
    resp = client.get('/api/v1/notifications/webhooks', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    assert resp.json()['total'] == 0

    # create
    create = client.post('/api/v1/notifications/webhooks', params={'tenant_id': 't1'}, json={
        'url': 'https://hooks.example.com/alert',
        'event_types': ['vuln_case_created', 'vuln_case_state_changed'],
        'enabled': True,
        'description': '??????',
    })
    assert create.status_code == 201
    sub_id = create.json()['sub_id']

    # list after create
    resp2 = client.get('/api/v1/notifications/webhooks', params={'tenant_id': 't1'})
    assert resp2.json()['total'] == 1

    # delete
    delete = client.delete(f'/api/v1/notifications/webhooks/{sub_id}', params={'tenant_id': 't1'})
    assert delete.status_code == 204
