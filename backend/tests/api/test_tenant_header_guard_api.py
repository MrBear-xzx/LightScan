from fastapi.testclient import TestClient

from app.db.session import get_engine
from app.main import app
from tests.api._vuln_case_test_helper import seed_case


def test_vuln_case_state_requires_header_tenant_match() -> None:
    seed_case(get_engine(), 7101, state='confirmed', tenant_id='t1')
    client = TestClient(app)
    response = client.patch(
        '/api/v1/vuln-cases/7101/state',
        params={'tenant_id': 't1'},
        headers={'X-Tenant-ID': 't2'},
        json={'new_state': 'in_progress'},
    )
    assert response.status_code == 403


def test_vuln_case_assign_requires_header_tenant_match() -> None:
    seed_case(get_engine(), 7102, state='confirmed', tenant_id='t1')
    client = TestClient(app)
    response = client.patch(
        '/api/v1/vuln-cases/7102/assign',
        params={'tenant_id': 't1'},
        headers={'X-Tenant-ID': 't2'},
        json={'owner': 'sec', 'sla_due_at': '2026-07-01T00:00:00Z'},
    )
    assert response.status_code == 403


def test_report_endpoints_require_header_tenant_match() -> None:
    client = TestClient(app)
    response = client.get(
        '/api/v1/reports/sla/overview',
        params={'tenant_id': 't1'},
        headers={'X-Tenant-ID': 't2'},
    )
    assert response.status_code == 403
