import hashlib

from app.plugins.base import ScannerPlugin


class NucleiJsonScannerPlugin(ScannerPlugin):
    def scan(self, asset: dict, policy: dict) -> list[dict]:
        return []

    def normalize(self, raw_result: dict) -> dict:
        if 'template-id' not in raw_result:
            raise ValueError('template-id is required')
        template_id = raw_result['template-id']
        severity = raw_result.get('info', {}).get('severity', 'medium')
        host = raw_result.get('host', '')
        matched_at = raw_result.get('matched-at', '')
        seed = f'{template_id}|{host}|{matched_at}'
        fingerprint = hashlib.sha256(seed.encode('utf-8')).hexdigest()

        return {
            'template_or_rule_id': template_id,
            'vuln_ref': template_id.upper(),
            'severity': severity,
            'confidence': 0.85,
            'evidence': matched_at or host,
            'fingerprint': fingerprint,
        }

    def health(self) -> dict:
        return {'status': 'healthy'}
