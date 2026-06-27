from app.plugins.registry import PluginRegistry
from app.plugins.discovery.http_probe import HttpProbeDiscoveryPlugin


def test_registry_executes_http_probe_plugin() -> None:
    registry = PluginRegistry()
    registry.register('http_probe', HttpProbeDiscoveryPlugin())

    plugin = registry.get('http_probe')
    assets = plugin.discover(['example.com'], {'resolve_dns': False})

    assert len(assets) == 1
    assert assets[0]['asset_type'] == 'domain'
    assert assets[0]['canonical_identifier'] == 'example.com'
