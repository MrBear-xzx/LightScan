from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.vuln_case import VulnCase


def test_correlation_empty() -> None:
    client = TestClient(app)
    resp = client.get('/api/v1/vuln-cases/correlation', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    body = resp.json()
    assert body['total_cases'] >= 0


def test_correlation_with_data() -> None:
    engine = get_engine()
    with Session(engine) as session:
        # Clear and insert seed data
        session.query(VulnCase).delete()
        session.add_all([
            VulnCase(tenant_id='t1', asset_id=1, normalized_vuln_key='CVE-001', risk_score=9.0, state='new'),
            VulnCase(tenant_id='t1', asset_id=1, normalized_vuln_key='CVE-002', risk_score=7.0, state='new'),
            VulnCase(tenant_id='t1', asset_id=2, normalized_vuln_key='CVE-003', risk_score=4.0, state='new'),
        ])
        session.commit()

    client = TestClient(app)
    resp = client.get('/api/v1/vuln-cases/correlation', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    body = resp.json()
    assert body['total_cases'] >= 3
    assert body['total_assets'] >= 2
