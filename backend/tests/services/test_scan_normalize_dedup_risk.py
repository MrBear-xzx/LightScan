from app.plugins.scanner.nuclei_json import NucleiJsonScannerPlugin
from app.services.risk_service import calculate_risk_score


def test_normalize_generates_fingerprint_and_risk_formula() -> None:
    plugin = NucleiJsonScannerPlugin()
    sample = {
        'template-id': 'cve-2023-0001',
        'info': {'severity': 'high'},
        'host': 'https://example.com',
        'matched-at': '/login',
    }
    normalized = plugin.normalize(sample)

    assert normalized['template_or_rule_id'] == 'cve-2023-0001'
    assert normalized['severity'] == 'high'
    assert normalized['fingerprint'] != ''

    score = calculate_risk_score(
        severity=8.0,
        asset_criticality=7.0,
        exposure=8.0,
        exploitability=6.0,
        compensating_control=2.0,
        weights={'a': 0.3, 'b': 0.25, 'c': 0.2, 'd': 0.2, 'e': 0.05},
    )
    assert round(score, 2) == 6.85
