from fastapi.testclient import TestClient

from app.main import app


def test_risk_rules_default() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/risk/rules', params={'tenant_id': 't1'})
    assert response.status_code == 200
    body = response.json()
    assert body['tenant_id'] == 't1'
    assert 'config' in body
    assert body['config']['weights']['severity_weight'] == 0.3


def test_risk_rules_upsert() -> None:
    client = TestClient(app)
    payload = {
        'severity_map': {
            'critical': 10.0, 'high': 8.0, 'medium': 5.0,
            'low': 2.0, 'unknown': 1.0,
        },
        'weights': {
            'severity_weight': 0.4,
            'asset_criticality_weight': 0.2,
            'exposure_weight': 0.2,
            'exploitability_weight': 0.15,
            'compensating_control_penalty': 0.05,
        },
        'thresholds': {
            'critical': 9.0, 'high': 7.0, 'medium': 4.0, 'low': 0.0,
        },
    }
    response = client.put('/api/v1/risk/rules', params={'tenant_id': 't1'}, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body['config']['weights']['severity_weight'] == 0.4


def test_risk_rules_persists_across_calls() -> None:
    client = TestClient(app)
    payload = {
        'severity_map': {'critical': 10.0, 'high': 8.0, 'medium': 5.0, 'low': 2.0, 'unknown': 1.0},
        'weights': {'severity_weight': 0.5, 'asset_criticality_weight': 0.2, 'exposure_weight': 0.1, 'exploitability_weight': 0.15, 'compensating_control_penalty': 0.05},
        'thresholds': {'critical': 9.0, 'high': 7.0, 'medium': 4.0, 'low': 0.0},
    }
    client.put('/api/v1/risk/rules', params={'tenant_id': 't1'}, json=payload)
    response = client.get('/api/v1/risk/rules', params={'tenant_id': 't1'})
    assert response.json()['config']['weights']['severity_weight'] == 0.5
