from fastapi.testclient import TestClient

from app.db.session import get_engine
from app.main import app
from tests.api._vuln_case_test_helper import seed_case


def test_sla_trend_returns_points() -> None:
    engine = get_engine()
    seed_case(engine, 4101, tenant_id='t1', state='confirmed', risk_score=8.0)
    seed_case(engine, 4102, tenant_id='t1', state='fixed', risk_score=5.0)

    client = TestClient(app)
    response = client.get('/api/v1/reports/sla/trend', params={'tenant_id': 't1', 'days': 7})
    assert response.status_code == 200

    body = response.json()
    assert body['tenant_id'] == 't1'
    assert body['days'] == 7
    assert len(body['points']) == 7
    assert {'date', 'overdue_cases', 'total_cases'} <= set(body['points'][0].keys())


def test_sla_trend_supports_time_range_and_week_granularity() -> None:
    engine = get_engine()
    seed_case(engine, 4201, tenant_id='t1', state='confirmed', risk_score=8.1)
    seed_case(engine, 4202, tenant_id='t1', state='reopened', risk_score=7.7)

    client = TestClient(app)
    response = client.get(
        '/api/v1/reports/sla/trend',
        params={
            'tenant_id': 't1',
            'days': 14,
            'granularity': 'week',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['days'] == 14
    assert body['granularity'] == 'week'
    assert len(body['points']) == 2
