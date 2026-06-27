from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event


def test_plugin_rollout_policy_can_be_upserted_and_queried() -> None:
    client = TestClient(app)
    initial_put = client.put(
        '/api/v1/plugins/rollout-policy',
        json={
            'tenant_id': 't1',
            'plugins': {
                'http_probe': {'status': 'enabled', 'rollout': 'stable'},
                'nuclei_json': {'status': 'disabled', 'rollout': 'canary'},
                'mockx_json': {'status': 'enabled', 'rollout': 'canary'},
            },
        },
    )
    assert initial_put.status_code == 200

    put = client.put(
        '/api/v1/plugins/rollout-policy',
        json={
            'tenant_id': 't1',
            'plugins': {
                'http_probe': {'status': 'enabled', 'rollout': 'stable'},
                'nuclei_json': {'status': 'enabled', 'rollout': 'stable'},
                'mockx_json': {'status': 'enabled', 'rollout': 'canary'},
            },
        },
    )
    assert put.status_code == 200
    put_body = put.json()
    assert put_body['plugins']['nuclei_json']['status'] == 'enabled'
    assert put_body['diff']['nuclei_json']['before']['status'] == 'disabled'
    assert put_body['diff']['nuclei_json']['after']['status'] == 'enabled'

    get_resp = client.get('/api/v1/plugins/rollout-policy', params={'tenant_id': 't1'})
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body['plugins']['http_probe']['rollout'] == 'stable'
    assert body['plugins']['mockx_json']['rollout'] == 'canary'


def test_plugin_rollout_policy_upsert_writes_audit_event() -> None:
    client = TestClient(app)
    response = client.put(
        '/api/v1/plugins/rollout-policy',
        json={
            'tenant_id': 't1',
            'plugins': {
                'http_probe': {'status': 'enabled', 'rollout': 'stable'},
                'nuclei_json': {'status': 'disabled', 'rollout': 'canary'},
                'mockx_json': {'status': 'enabled', 'rollout': 'canary'},
            },
        },
    )
    assert response.status_code == 200

    engine = get_engine()
    with Session(engine) as session:
        event = session.execute(
            select(Event)
            .where(Event.tenant_id == 't1')
            .where(Event.event_type == 'plugin_rollout_policy_updated')
            .order_by(Event.event_id.desc())
            .limit(1)
        ).scalar_one_or_none()
        assert event is not None
        assert event.reference_id == 't1'
        assert '"nuclei_json"' in event.payload_json


def test_rollout_policy_change_affects_plugin_list_and_health() -> None:
    client = TestClient(app)
    put = client.put(
        '/api/v1/plugins/rollout-policy',
        json={
            'tenant_id': 't1',
            'plugins': {
                'http_probe': {'status': 'enabled', 'rollout': 'stable'},
                'nuclei_json': {'status': 'enabled', 'rollout': 'canary'},
                'mockx_json': {'status': 'disabled', 'rollout': 'canary'},
            },
        },
    )
    assert put.status_code == 200

    enabled_list = client.get('/api/v1/plugins', params={'tenant_id': 't1', 'status': 'enabled'})
    assert enabled_list.status_code == 200
    enabled_ids = {item['plugin_id'] for item in enabled_list.json()['items']}
    assert 'nuclei_json' in enabled_ids
    assert 'mockx_json' not in enabled_ids

    health = client.get('/api/v1/plugins/health', params={'tenant_id': 't1'})
    assert health.status_code == 200
    body = health.json()
    assert body['total'] == len(enabled_ids)


def test_plugin_rollout_policy_rejects_unknown_plugin() -> None:
    client = TestClient(app)
    response = client.put(
        '/api/v1/plugins/rollout-policy',
        json={
            'tenant_id': 't1',
            'plugins': {
                'http_probe': {'status': 'enabled', 'rollout': 'stable'},
                'unknown_plugin': {'status': 'enabled', 'rollout': 'canary'},
            },
        },
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'unknown plugin in rollout policy'


def test_plugin_rollout_audit_list_returns_latest_items() -> None:
    client = TestClient(app)
    update_response = client.put(
        '/api/v1/plugins/rollout-policy',
        json={
            'tenant_id': 't1',
            'plugins': {
                'http_probe': {'status': 'enabled', 'rollout': 'stable'},
                'nuclei_json': {'status': 'disabled', 'rollout': 'canary'},
                'mockx_json': {'status': 'enabled', 'rollout': 'canary'},
            },
        },
    )
    assert update_response.status_code == 200

    response = client.get('/api/v1/plugins/rollout-audit', params={'tenant_id': 't1', 'limit': 5})
    assert response.status_code == 200
    body = response.json()
    assert body['tenant_id'] == 't1'
    assert body['total'] >= 1
    assert body['items'][0]['event_type'] == 'plugin_rollout_policy_updated'
    assert 'plugins' in body['items'][0]['payload']


def test_plugin_rollout_audit_supports_pagination() -> None:
    client = TestClient(app)
    for idx in range(3):
        response = client.put(
            '/api/v1/plugins/rollout-policy',
            json={
                'tenant_id': 't1',
                'plugins': {
                    'http_probe': {'status': 'enabled', 'rollout': 'stable'},
                    'nuclei_json': {'status': 'disabled', 'rollout': 'canary'},
                    'mockx_json': {'status': 'enabled', 'rollout': 'canary'},
                },
            },
        )
        assert response.status_code == 200

    page1 = client.get(
        '/api/v1/plugins/rollout-audit',
        params={'tenant_id': 't1', 'page': 1, 'page_size': 2},
    )
    assert page1.status_code == 200
    body1 = page1.json()
    assert body1['page'] == 1
    assert body1['page_size'] == 2
    assert body1['total'] >= 3
    assert len(body1['items']) == 2

    page2 = client.get(
        '/api/v1/plugins/rollout-audit',
        params={'tenant_id': 't1', 'page': 2, 'page_size': 2},
    )
    assert page2.status_code == 200
    body2 = page2.json()
    assert body2['page'] == 2
    assert body2['page_size'] == 2
    assert body2['total'] >= 3
    assert len(body2['items']) >= 1


def test_plugin_rollout_audit_supports_time_window_filter() -> None:
    client = TestClient(app)
    put = client.put(
        '/api/v1/plugins/rollout-policy',
        json={
            'tenant_id': 't1',
            'plugins': {
                'http_probe': {'status': 'enabled', 'rollout': 'stable'},
                'nuclei_json': {'status': 'disabled', 'rollout': 'canary'},
                'mockx_json': {'status': 'enabled', 'rollout': 'canary'},
            },
        },
    )
    assert put.status_code == 200

    engine = get_engine()
    with Session(engine) as session:
        event = session.execute(
            select(Event)
            .where(Event.tenant_id == 't1')
            .where(Event.event_type == 'plugin_rollout_policy_updated')
            .order_by(Event.event_id.desc())
            .limit(1)
        ).scalar_one()
        old_time = '2020-01-01T00:00:00+00:00'
        session.execute(
            update(Event)
            .where(Event.event_id == event.event_id)
            .values(created_at=old_time),
        )
        session.commit()

    response = client.get(
        '/api/v1/plugins/rollout-audit',
        params={
            'tenant_id': 't1',
            'requested_from': '2025-01-01T00:00:00Z',
            'requested_to': '2025-12-31T23:59:59Z',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 0
    assert body['items'] == []


def test_plugin_rollout_audit_rejects_invalid_time_window() -> None:
    client = TestClient(app)
    response = client.get(
        '/api/v1/plugins/rollout-audit',
        params={
            'tenant_id': 't1',
            'requested_from': '2026-01-02T00:00:00Z',
            'requested_to': '2026-01-01T00:00:00Z',
        },
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'requested_from must be earlier than requested_to'


def test_plugin_rollout_audit_supports_event_type_filter() -> None:
    client = TestClient(app)
    put = client.put(
        '/api/v1/plugins/rollout-policy',
        json={
            'tenant_id': 't1',
            'plugins': {
                'http_probe': {'status': 'enabled', 'rollout': 'stable'},
                'nuclei_json': {'status': 'disabled', 'rollout': 'canary'},
                'mockx_json': {'status': 'enabled', 'rollout': 'canary'},
            },
        },
    )
    assert put.status_code == 200

    response = client.get(
        '/api/v1/plugins/rollout-audit',
        params={
            'tenant_id': 't1',
            'event_type': 'notification_dispatched',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 0
    assert body['items'] == []


def test_plugin_rollout_audit_supports_plugin_id_filter() -> None:
    client = TestClient(app)
    put = client.put(
        '/api/v1/plugins/rollout-policy',
        json={
            'tenant_id': 't1',
            'plugins': {
                'http_probe': {'status': 'enabled', 'rollout': 'stable'},
                'nuclei_json': {'status': 'disabled', 'rollout': 'canary'},
                'mockx_json': {'status': 'enabled', 'rollout': 'canary'},
            },
        },
    )
    assert put.status_code == 200

    response = client.get(
        '/api/v1/plugins/rollout-audit',
        params={
            'tenant_id': 't1',
            'plugin_id': 'not-exists-plugin',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 0
    assert body['items'] == []
