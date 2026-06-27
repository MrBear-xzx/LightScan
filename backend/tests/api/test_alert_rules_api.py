from fastapi.testclient import TestClient

from app.main import app


def test_alert_rules_empty() -> None:
    client = TestClient(app)
    resp = client.get('/api/v1/ops/alert-rules', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    assert resp.json()['total'] == 0


def test_alert_rule_crud() -> None:
    client = TestClient(app)
    payload = {
        'name': 'high-task-failure',
        'enabled': True,
        'severity': 'critical',
        'metrics': [
            {'metric_name': 'lightscan_tasks_total', 'operator': '>', 'threshold': 100, 'duration_seconds': 300},
        ],
        'description': '???????',
    }
    create = client.post('/api/v1/ops/alert-rules', params={'tenant_id': 't1'}, json=payload)
    assert create.status_code == 201
    rule_id = create.json()['rule_id']
    assert create.json()['config']['name'] == 'high-task-failure'

    get = client.get(f'/api/v1/ops/alert-rules/{rule_id}', params={'tenant_id': 't1'})
    assert get.status_code == 200
    assert get.json()['config']['severity'] == 'critical'

    delete = client.delete(f'/api/v1/ops/alert-rules/{rule_id}', params={'tenant_id': 't1'})
    assert delete.status_code == 204

    get_after = client.get(f'/api/v1/ops/alert-rules/{rule_id}', params={'tenant_id': 't1'})
    assert get_after.status_code == 404


def test_alert_rule_delete_nonexistent() -> None:
    client = TestClient(app)
    resp = client.delete('/api/v1/ops/alert-rules/999999', params={'tenant_id': 't1'})
    assert resp.status_code == 404
