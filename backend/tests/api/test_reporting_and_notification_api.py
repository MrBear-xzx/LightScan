from fastapi.testclient import TestClient

from app.db.session import get_engine
from app.main import app
from tests.api._vuln_case_test_helper import seed_case


def test_vuln_report_summary_counts_by_state() -> None:
    engine = get_engine()
    seed_case(engine, 1101, state='confirmed', tenant_id='t1', risk_score=9.0)
    seed_case(engine, 1102, state='reopened', tenant_id='t1', risk_score=8.0)
    seed_case(engine, 1103, state='fixed', tenant_id='t1', risk_score=5.0)
    seed_case(engine, 1104, state='new', tenant_id='t2', risk_score=9.9)

    client = TestClient(app)
    response = client.get('/api/v1/reports/vuln/summary', params={'tenant_id': 't1'})
    assert response.status_code == 200
    body = response.json()
    assert body['tenant_id'] == 't1'
    assert body['counts'] == {
        'new': 0,
        'confirmed': 1,
        'in_progress': 0,
        'fixed': 1,
        'ignored': 0,
        'reopened': 1,
    }


def test_notify_preview_returns_pending_messages() -> None:
    engine = get_engine()
    seed_case(engine, 1201, state='confirmed', tenant_id='t1', risk_score=9.2, owner='alice')
    seed_case(engine, 1202, state='reopened', tenant_id='t1', risk_score=8.1, owner=None)
    seed_case(engine, 1203, state='fixed', tenant_id='t1', risk_score=9.8, owner='bob')
    seed_case(engine, 1204, state='confirmed', tenant_id='t1', risk_score=6.0, owner='carol')
    seed_case(engine, 1205, state='new', tenant_id='t2', risk_score=9.9, owner='team2')

    client = TestClient(app)
    response = client.get('/api/v1/notifications/preview', params={'tenant_id': 't1', 'min_risk_score': 7.0})
    assert response.status_code == 200
    body = response.json()
    assert body['tenant_id'] == 't1'
    assert [item['case_id'] for item in body['items']] == [1201, 1202]
    assert [item['risk_score'] for item in body['items']] == [9.2, 8.1]
