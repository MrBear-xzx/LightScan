from sqlalchemy.orm import Session

from app.models.finding import Finding


def persist_findings(session: Session, tenant_id: str, asset_id: int, plugin_id: str, normalized: list[dict]) -> list[Finding]:
    saved: list[Finding] = []
    for item in normalized:
        finding = Finding(
            tenant_id=tenant_id,
            asset_id=asset_id,
            plugin_id=plugin_id,
            template_or_rule_id=item['template_or_rule_id'],
            vuln_ref=item['vuln_ref'],
            severity=item['severity'],
            confidence=item['confidence'],
            evidence=item['evidence'],
            fingerprint=item['fingerprint'],
        )
        session.add(finding)
        saved.append(finding)
    session.commit()
    return saved
