from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.finding import Finding
from app.models.vuln_case import VulnCase


def upsert_vuln_case_from_finding(session: Session, finding: Finding, risk_score: float) -> VulnCase:
    stmt = select(VulnCase).where(
        VulnCase.tenant_id == finding.tenant_id,
        VulnCase.asset_id == finding.asset_id,
        VulnCase.normalized_vuln_key == finding.fingerprint,
    )
    existing = session.execute(stmt).scalar_one_or_none()

    if existing is not None:
        existing.risk_score = risk_score
        session.commit()
        session.refresh(existing)
        return existing

    case = VulnCase(
        tenant_id=finding.tenant_id,
        asset_id=finding.asset_id,
        normalized_vuln_key=finding.fingerprint,
        risk_score=risk_score,
        state='new',
    )
    session.add(case)
    session.commit()
    session.refresh(case)
    return case
