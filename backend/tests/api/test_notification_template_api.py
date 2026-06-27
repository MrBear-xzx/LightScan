from fastapi.testclient import TestClient

from app.main import app
from app.services.notification_template_service import render_template
from app.schemas.notification_template import NotificationTemplate


def test_template_crud() -> None:
    client = TestClient(app)

    # list empty
    resp = client.get('/api/v1/notifications/templates', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    assert resp.json()['total'] == 0

    # create
    create = client.post('/api/v1/notifications/templates', params={'tenant_id': 't1'}, json={
        'name': 'vuln-alert', 'provider': 'dingtalk',
        'title_template': '???? #{case_id}',
        'body_template': '????: {risk_score}',
    })
    assert create.status_code == 201
    tid = create.json()['template_id']

    # get
    get = client.get(f'/api/v1/notifications/templates/{tid}', params={'tenant_id': 't1'})
    assert get.status_code == 200

    # delete
    delete = client.delete(f'/api/v1/notifications/templates/{tid}', params={'tenant_id': 't1'})
    assert delete.status_code == 204


def test_render_template() -> None:
    tpl = NotificationTemplate(
        name='test', provider='webhook',
        title_template='?? #{case_id} - {severity}',
        body_template='??: {risk_score}',
    )
    title, body = render_template(tpl, {'case_id': 42, 'severity': 'high', 'risk_score': 8.5})
    assert title == '?? #42 - high'
    assert body == '??: 8.5'
