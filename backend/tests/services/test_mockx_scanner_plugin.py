from app.plugins.scanner.mockx_json import MockXJsonScannerPlugin


def test_mockx_scanner_normalize_returns_standard_fields() -> None:
    plugin = MockXJsonScannerPlugin()
    normalized = plugin.normalize(
        {
            'rule_id': 'mockx-001',
            'severity': 'low',
            'target': 'https://example.com',
            'evidence': '/.env',
        }
    )

    assert normalized['template_or_rule_id'] == 'mockx-001'
    assert normalized['vuln_ref'] == 'MOCKX-001'
    assert normalized['severity'] == 'low'
    assert normalized['fingerprint']


def test_mockx_scanner_health_is_healthy() -> None:
    plugin = MockXJsonScannerPlugin()
    assert plugin.health()['status'] == 'healthy'
