from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vuln_case import VulnCase
from app.services.event_service import log_event_with_session


def sync_tickets(session: Session, tenant_id: str, provider: str, case_ids: list[int]) -> int:
    rows = session.execute(
        select(VulnCase)
        .where(VulnCase.tenant_id == tenant_id)
        .where(VulnCase.case_id.in_(case_ids))
    ).scalars().all()

    for row in rows:
        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type='ticket_synced',
            reference_id=str(row.case_id),
            payload={
                'provider': provider,
                'case_id': row.case_id,
                'owner': row.owner,
                'state': row.state,
            },
        )

    session.commit()
    return len(rows)
