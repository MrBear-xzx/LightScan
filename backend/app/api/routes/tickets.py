from fastapi import APIRouter, Header
from sqlalchemy.orm import Session

from app.api.tenant_guard import validate_tenant_guard
from app.db.session import get_engine
from app.schemas.ticket import TicketSyncRequest, TicketSyncResponse
from app.services.event_service import log_event_with_session
from app.services.ticket_service import sync_tickets
from app.workers.jobs import ticket_sync_job

router = APIRouter(prefix='/api/v1/tickets', tags=['tickets'])


@router.post('/sync', response_model=TicketSyncResponse, summary='工单同步（Mock）')
def ticket_sync(
    payload: TicketSyncRequest,
    x_tenant_id: str | None = Header(default=None, alias='X-Tenant-ID'),
) -> TicketSyncResponse:
    tenant_id = validate_tenant_guard(payload.tenant_id, x_tenant_id)

    if payload.mode == 'async':
        task = ticket_sync_job.delay(tenant_id, payload.provider, payload.case_ids)
        engine = get_engine()
        with Session(engine) as session:
            log_event_with_session(
                session,
                tenant_id=tenant_id,
                event_type='ticket_sync_async_queued',
                reference_id=task.id,
                payload={
                    'provider': payload.provider,
                    'case_ids': payload.case_ids,
                },
            )
            session.commit()
        return TicketSyncResponse(
            tenant_id=tenant_id,
            provider=payload.provider,
            mode='async',
            job_id=task.id,
            synced=0,
        )

    engine = get_engine()
    with Session(engine) as session:
        synced = sync_tickets(session, tenant_id, payload.provider, payload.case_ids)

    return TicketSyncResponse(
        tenant_id=tenant_id,
        provider=payload.provider,
        mode='sync',
        synced=synced,
    )
