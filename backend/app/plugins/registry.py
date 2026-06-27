from dataclasses import dataclass
from typing import Literal

from app.core.plugin_rollout import get_plugin_rollout
from app.plugins.discovery.http_probe import HttpProbeDiscoveryPlugin
from app.plugins.scanner.mockx_json import MockXJsonScannerPlugin
from app.plugins.scanner.nuclei_json import NucleiJsonScannerPlugin

PluginKind = Literal['discovery', 'scanner']


@dataclass
class PluginMeta:
    plugin_id: str
    kind: PluginKind
    version: str
    capabilities: list[str]
    status: str
    rollout: str
    plugin: object


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginMeta] = {}

    def register(
        self,
        plugin_id: str,
        plugin: object,
        *,
        kind: PluginKind = 'discovery',
        version: str = '0.1.0',
        capabilities: list[str] | None = None,
        status: str = 'enabled',
        rollout: str = 'stable',
    ) -> None:
        self._plugins[plugin_id] = PluginMeta(
            plugin_id=plugin_id,
            kind=kind,
            version=version,
            capabilities=capabilities or [],
            status=status,
            rollout=rollout,
            plugin=plugin,
        )

    def get(self, plugin_id: str) -> object:
        if plugin_id not in self._plugins:
            raise KeyError(f'plugin not found: {plugin_id}')
        return self._plugins[plugin_id].plugin

    def list_plugins(self, capability: str | None = None, status: str | None = None) -> list[PluginMeta]:
        items = list(self._plugins.values())
        if capability:
            items = [item for item in items if capability in item.capabilities]
        if status:
            items = [item for item in items if item.status == status]
        return items


def build_default_registry(tenant_id: str = 'default') -> PluginRegistry:
    registry = PluginRegistry()
    http_probe_rollout = get_plugin_rollout('http_probe', tenant_id)
    registry.register(
        'http_probe',
        HttpProbeDiscoveryPlugin(),
        kind='discovery',
        version='0.1.0',
        capabilities=['discover'],
        status=http_probe_rollout['status'],
        rollout=http_probe_rollout['rollout'],
    )
    nuclei_rollout = get_plugin_rollout('nuclei_json', tenant_id)
    registry.register(
        'nuclei_json',
        NucleiJsonScannerPlugin(),
        kind='scanner',
        version='0.1.0',
        capabilities=['scan', 'normalize'],
        status=nuclei_rollout['status'],
        rollout=nuclei_rollout['rollout'],
    )
    mockx_rollout = get_plugin_rollout('mockx_json', tenant_id)
    registry.register(
        'mockx_json',
        MockXJsonScannerPlugin(),
        kind='scanner',
        version='0.1.0',
        capabilities=['scan', 'normalize'],
        status=mockx_rollout['status'],
        rollout=mockx_rollout['rollout'],
    )
    return registry
