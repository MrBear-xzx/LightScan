from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.vuln_case import VulnCase


def test_lifecycle_empty() -> None:
    client = TestClient(app)
    resp = client.get('/api/v1/reports/vuln/lifecycle', params={'tenant_id': 't_empty'})
    assert resp.status_code == 200
    body = resp.json()
    assert body['total_cases'] == 0


def test_lifecycle_with_data() -> None:
    engine = get_engine()
    with Session(engine) as session:
        session.query(VulnCase).delete()
        session.add_all([
            VulnCase(tenant_id='t1', asset_id=1, normalized_vuln_key='k1', risk_score=5.0, state='new'),
            VulnCase(tenant_id='t1', asset_id=1, normalized_vuln_key='k2', risk_score=5.0, state='in_progress'),
            VulnCase(tenant_id='t1', asset_id=2, normalized_vuln_key='k3', risk_score=5.0, state='resolved'),
        ])
        session.commit()

    client = TestClient(app)
    resp = client.get('/api/v1/reports/vuln/lifecycle', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    body = resp.json()
    assert body['total_cases'] >= 3
    assert body['total_open'] >= 2
    assert body['state_distribution']['new'] >= 1
    assert body['state_distribution']['resolved'] >= 1
