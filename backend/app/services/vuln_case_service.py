from datetime import datetime, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.vuln_case import VulnCase
from app.services.event_service import log_event


ORDER_BY_FIELDS = {
    'risk_score': VulnCase.risk_score,
    'sla_due_at': VulnCase.sla_due_at,
    'created_at': VulnCase.created_at,
}


def query_cases(
    session: Session,
    *,
    tenant_id: str,
    state: str | None,
    owner: str | None,
    overdue_only: bool,
    sort_by: str,
    sort_order: str,
    page: int,
    page_size: int,
) -> tuple[int, list[VulnCase]]:
    stmt: Select[tuple[VulnCase]] = select(VulnCase).where(VulnCase.tenant_id == tenant_id)
    if state:
        stmt = stmt.where(VulnCase.state == state)
    if owner:
        stmt = stmt.where(VulnCase.owner == owner)
    if overdue_only:
        stmt = stmt.where(
            VulnCase.sla_due_at.is_not(None),
            VulnCase.sla_due_at < datetime.now(timezone.utc),
        )

    order_col = ORDER_BY_FIELDS[sort_by]
    stmt = stmt.order_by(order_col.desc() if sort_order == 'desc' else order_col.asc())

    total = session.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    rows = session.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    return total, rows


def assign_case(
    session: Session,
    *,
    tenant_id: str,
    case_id: int,
    owner: str,
    sla_due_at: datetime | None,
) -> VulnCase:
    case = session.execute(
        select(VulnCase).where(
            VulnCase.case_id == case_id,
            VulnCase.tenant_id == tenant_id,
        )
    ).scalar_one_or_none()
    if case is None:
        raise ValueError('not_found')

    case.owner = owner
    case.sla_due_at = sla_due_at
    session.flush()
    log_event(
        session.connection(),
        tenant_id=case.tenant_id,
        event_type='vuln_case_assigned',
        reference_id=str(case.case_id),
        payload={
            'owner': owner,
            'sla_due_at': sla_due_at.isoformat() if sla_due_at else None,
        },
    )
    session.commit()
    return case
