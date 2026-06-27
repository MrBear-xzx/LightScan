from fastapi.testclient import TestClient

from app.main import app


def test_scheduled_reports_crud() -> None:
    client = TestClient(app)

    # list empty
    resp = client.get('/api/v1/reports/scheduled', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    assert resp.json()['total'] == 0

    # create
    create = client.post('/api/v1/reports/scheduled', params={'tenant_id': 't1'}, json={
        'name': 'weekly-vuln-summary',
        'report_type': 'vuln_summary',
        'cron_expression': '0 9 * * 1',
        'provider': 'dingtalk',
        'webhook_url': 'https://oapi.dingtalk.com/robot/send',
        'enabled': True,
        'description': '??????',
    })
    assert create.status_code == 201
    rid = create.json()['report_id']

    # list after
    resp2 = client.get('/api/v1/reports/scheduled', params={'tenant_id': 't1'})
    assert resp2.json()['total'] == 1

    # delete
    delete = client.delete(f'/api/v1/reports/scheduled/{rid}', params={'tenant_id': 't1'})
    assert delete.status_code == 204
