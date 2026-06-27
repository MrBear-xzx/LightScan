from fastapi.testclient import TestClient

from app.db.session import get_engine
from app.main import app
from tests.api._vuln_case_test_helper import seed_case


def test_notification_policy_can_be_upserted_and_queried() -> None:
    client = TestClient(app)
    put = client.put(
        '/api/v1/notifications/policy',
        json={
            'tenant_id': 't1',
            'dedup_window_minutes': 45,
            'dedup_policy_by_risk': {'high': 90, 'medium': 15, 'low': 5},
        },
    )
    assert put.status_code == 200
    put_body = put.json()
    assert put_body['dedup_window_minutes'] == 45

    get_resp = client.get('/api/v1/notifications/policy', params={'tenant_id': 't1'})
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body['dedup_window_minutes'] == 45
    assert body['dedup_policy_by_risk']['high'] == 90


def test_notification_dispatch_uses_tenant_policy_when_request_omits_dedup_params() -> None:
    engine = get_engine()
    seed_case(engine, 9501, state='confirmed', tenant_id='t1', risk_score=9.2, owner='alice')
    seed_case(engine, 9502, state='confirmed', tenant_id='t1', risk_score=6.3, owner='bob')

    client = TestClient(app)
    set_policy = client.put(
        '/api/v1/notifications/policy',
        json={
            'tenant_id': 't1',
            'dedup_window_minutes': 30,
            'dedup_policy_by_risk': {'high': 60, 'medium': 0, 'low': 0},
        },
    )
    assert set_policy.status_code == 200

    first = client.post(
        '/api/v1/notifications/dispatch',
        json={'tenant_id': 't1', 'min_risk_score': 5.0},
    )
    assert first.status_code == 200
    assert first.json()['dispatched'] == 2

    second = client.post(
        '/api/v1/notifications/dispatch',
        json={'tenant_id': 't1', 'min_risk_score': 5.0},
    )
    assert second.status_code == 200
    second_body = second.json()
    assert second_body['dispatched'] == 1
    assert second_body['suppressed'] == 1
