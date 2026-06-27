from app.plugins.base import DiscoveryPlugin


class HttpProbeDiscoveryPlugin(DiscoveryPlugin):
    def discover(self, targets: list[str], policy: dict) -> list[dict]:
        discovered: list[dict] = []
        default_criticality = int(policy.get('default_criticality', 3))
        for target in targets:
            if not target.strip():
                raise ValueError('target must not be empty')
            is_ip = all(part.isdigit() for part in target.split('.')) and len(target.split('.')) == 4
            asset_type = 'ip' if is_ip else 'domain'
            discovered.append(
                {
                    'asset_type': asset_type,
                    'canonical_identifier': target,
                    'criticality': default_criticality,
                }
            )
        return discovered

    def health(self) -> dict:
        return {'status': 'healthy'}
