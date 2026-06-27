from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.finding import Finding


def _seed_findings() -> None:
    engine = get_engine()
    with Session(engine) as session:
        for item in [
            {'tenant_id': 't1', 'asset_id': 1, 'plugin_id': 'nuclei_json',
             'template_or_rule_id': 'cve-001', 'vuln_ref': 'CVE-001',
             'severity': 'high', 'confidence': 0.9, 'evidence': 'x',
             'fingerprint': 'fp1'},
            {'tenant_id': 't1', 'asset_id': 1, 'plugin_id': 'http_probe',
             'template_or_rule_id': 'tcp-001', 'vuln_ref': 'TCP-001',
             'severity': 'medium', 'confidence': 0.8, 'evidence': 'y',
             'fingerprint': 'fp2'},
            {'tenant_id': 't1', 'asset_id': 2, 'plugin_id': 'nuclei_json',
             'template_or_rule_id': 'cve-002', 'vuln_ref': 'CVE-002',
             'severity': 'critical', 'confidence': 0.95, 'evidence': 'z',
             'fingerprint': 'fp3'},
        ]:
            session.add(Finding(**item))
        session.commit()


def test_scan_aggregation_returns_grouped_results() -> None:
    _seed_findings()
    client = TestClient(app)
    response = client.get('/api/v1/scan/aggregation', params={'tenant_id': 't1'})
    assert response.status_code == 200
    body = response.json()
    assert body['tenant_id'] == 't1'
    assert body['total_findings'] >= 3
    assert body['total_assets'] >= 2
    assert body['severity_breakdown']['high'] >= 1
    assert body['severity_breakdown']['critical'] >= 1
    assert len(body['assets']) >= 2


def test_scan_aggregation_returns_empty_for_unknown_tenant() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/scan/aggregation', params={'tenant_id': 'unknown'})
    assert response.status_code == 200
    body = response.json()
    assert body['total_findings'] == 0
    assert body['total_assets'] == 0
    assert body['assets'] == []
