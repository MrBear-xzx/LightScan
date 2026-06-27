import hashlib

from app.plugins.base import ScannerPlugin


class MockXJsonScannerPlugin(ScannerPlugin):
    def scan(self, asset: dict, policy: dict) -> list[dict]:
        return []

    def normalize(self, raw_result: dict) -> dict:
        rule_id = str(raw_result.get('rule_id', '')).strip()
        if not rule_id:
            raise ValueError('rule_id is required')
        severity = str(raw_result.get('severity', 'medium'))
        target = str(raw_result.get('target', ''))
        evidence = str(raw_result.get('evidence', ''))
        seed = f'{rule_id}|{target}|{evidence}'
        fingerprint = hashlib.sha256(seed.encode('utf-8')).hexdigest()
        return {
            'template_or_rule_id': rule_id,
            'vuln_ref': rule_id.upper(),
            'severity': severity,
            'confidence': 0.8,
            'evidence': evidence or target,
            'fingerprint': fingerprint,
        }

    def health(self) -> dict:
        return {'status': 'healthy'}
