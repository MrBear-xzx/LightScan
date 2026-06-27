import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.event import Event
from app.schemas.operation_log import OperationLogItem, OperationLogResponse


def query_operation_logs(
    tenant_id: str,
    page: int = 1,
    page_size: int = 20,
    event_type: str | None = None,
) -> OperationLogResponse:
    engine = get_engine()
    with Session(engine) as session:
        base = select(Event).where(Event.tenant_id == tenant_id)
        if event_type:
            base = base.where(Event.event_type == event_type)

        total = session.execute(
            select(func.count()).select_from(base.subquery())
        ).scalar_one()

        offset = (page - 1) * page_size
        rows = session.execute(
            base.order_by(Event.event_id.desc()).offset(offset).limit(page_size)
        ).scalars().all()

        items = [
            OperationLogItem(
                event_id=row.event_id,
                tenant_id=row.tenant_id,
                event_type=row.event_type,
                reference_id=row.reference_id,
                payload=json.loads(row.payload_json),
                created_at=row.created_at.isoformat(),
            )
            for row in rows
        ]

    return OperationLogResponse(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        total=total,
        items=items,
    )
