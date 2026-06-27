from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.session import get_engine
from app.main import app
from tests.api._vuln_case_test_helper import seed_case


def test_sla_overview_aggregates_by_tenant() -> None:
    engine = get_engine()
    now = datetime.now(timezone.utc)

    # t1 数据
    seed_case(engine, 3101, state='confirmed', tenant_id='t1', risk_score=8.0, sla_due_at=now - timedelta(hours=2))
    seed_case(engine, 3102, state='in_progress', tenant_id='t1', risk_score=7.5, sla_due_at=now + timedelta(hours=24))
    seed_case(engine, 3103, state='confirmed', tenant_id='t1', risk_score=6.0, sla_due_at=now + timedelta(days=5))
    seed_case(engine, 3104, state='new', tenant_id='t1', risk_score=5.0, sla_due_at=None)
    seed_case(engine, 3105, state='fixed', tenant_id='t1', risk_score=9.0, sla_due_at=now - timedelta(days=1))

    # t2 数据（不应被统计）
    seed_case(engine, 3201, state='confirmed', tenant_id='t2', risk_score=9.9, sla_due_at=now - timedelta(days=1))

    client = TestClient(app)
    response = client.get('/api/v1/reports/sla/overview', params={'tenant_id': 't1'})
    assert response.status_code == 200

    body = response.json()
    assert body['tenant_id'] == 't1'
    assert body['total_cases'] == 5
    assert body['overdue_cases'] == 1
    assert body['due_48h_cases'] == 1
    assert body['no_sla_cases'] == 1
    assert body['status_counts']['confirmed'] == 2
    assert body['status_counts']['in_progress'] == 1
    assert body['status_counts']['fixed'] == 1
    assert body['status_counts']['new'] == 1
