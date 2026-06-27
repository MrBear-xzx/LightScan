from sqlalchemy.orm import Session

from app.models.vuln_case import VulnCase


def seed_case(
    engine,
    case_id: int,
    state: str = 'confirmed',
    owner: str | None = None,
    risk_score: float = 1.0,
    tenant_id: str = 't1',
    asset_id: int = 1,
    normalized_vuln_key: str = 'fp',
    sla_due_at=None,
) -> None:
    with Session(engine) as session:
        existing = session.get(VulnCase, case_id)
        if existing is None:
            case = VulnCase(
                case_id=case_id,
                tenant_id=tenant_id,
                asset_id=asset_id,
                normalized_vuln_key=normalized_vuln_key,
                risk_score=risk_score,
                state=state,
                owner=owner,
                sla_due_at=sla_due_at,
            )
            session.add(case)
        else:
            existing.state = state
            existing.owner = owner
            existing.risk_score = risk_score
            existing.sla_due_at = sla_due_at
        session.commit()
