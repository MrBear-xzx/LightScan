import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.policy import Policy
from app.schemas.scheduled_report import (
    ScheduledReportConfig,
    ScheduledReportListResponse,
    ScheduledReportResponse,
)

_REPORT_PREFIX = 'scheduled_report_'


def list_reports(tenant_id: str) -> ScheduledReportListResponse:
    engine = get_engine()
    with Session(engine) as session:
        rows = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.name.like(_REPORT_PREFIX + '%'))
            .order_by(Policy.policy_id.desc())
        ).scalars().all()
        items = [_row_to_response(r) for r in rows]
        return ScheduledReportListResponse(tenant_id=tenant_id, total=len(items), items=items)


def create_report(tenant_id: str, config: ScheduledReportConfig) -> ScheduledReportResponse:
    engine = get_engine()
    full_name = _REPORT_PREFIX + config.name
    with Session(engine) as session:
        row = Policy(
            tenant_id=tenant_id,
            name=full_name,
            config_json=json.dumps(config.model_dump(), ensure_ascii=False),
        )
        session.add(row)
        session.commit()
        session.refresh(row)
    return _row_to_response(row)


def delete_report(tenant_id: str, report_id: int) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.policy_id == report_id)
            .where(Policy.name.like(_REPORT_PREFIX + '%'))
        ).scalar_one_or_none()
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True


def _row_to_response(row: Policy) -> ScheduledReportResponse:
    config = ScheduledReportConfig(**json.loads(row.config_json))
    return ScheduledReportResponse(report_id=row.policy_id, tenant_id=row.tenant_id, config=config)
