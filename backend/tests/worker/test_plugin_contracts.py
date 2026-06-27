import pytest

from app.plugins.discovery.http_probe import HttpProbeDiscoveryPlugin
from app.plugins.scanner.nuclei_json import NucleiJsonScannerPlugin


def test_discovery_plugin_contract_includes_health() -> None:
    plugin = HttpProbeDiscoveryPlugin()
    assets = plugin.discover(['example.com', '198.51.100.10'], {'default_criticality': 3})

    assert len(assets) == 2
    assert all('asset_type' in item for item in assets)
    assert all('canonical_identifier' in item for item in assets)

    health = plugin.health()
    assert health['status'] == 'healthy'


def test_scanner_plugin_contract_includes_scan_normalize_health() -> None:
    plugin = NucleiJsonScannerPlugin()

    scan_output = plugin.scan({'asset_id': 'a1'}, {'mode': 'quick'})
    assert isinstance(scan_output, list)

    normalized = plugin.normalize(
        {
            'template-id': 'cve-2026-0001',
            'info': {'severity': 'medium'},
            'host': 'https://example.com',
            'matched-at': '/admin',
        }
    )
    assert normalized['template_or_rule_id'] == 'cve-2026-0001'
    assert normalized['fingerprint']

    health = plugin.health()
    assert health['status'] == 'healthy'


def test_scanner_plugin_normalize_rejects_invalid_payload() -> None:
    plugin = NucleiJsonScannerPlugin()
    with pytest.raises(ValueError, match='template-id is required'):
        plugin.normalize({'host': 'https://example.com'})


def test_discovery_plugin_rejects_empty_target() -> None:
    plugin = HttpProbeDiscoveryPlugin()
    with pytest.raises(ValueError, match='target must not be empty'):
        plugin.discover([''], {'default_criticality': 3})
