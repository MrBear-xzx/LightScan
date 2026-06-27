from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.scan_task import ScanTask
from app.services.event_service import log_event_with_session


def cancel_scan_task(tenant_id: str, task_id: int) -> dict | None:
    engine = get_engine()
    with Session(engine) as session:
        task = session.execute(
            select(ScanTask)
            .where(ScanTask.tenant_id == tenant_id)
            .where(ScanTask.task_id == task_id)
        ).scalar_one_or_none()
        if task is None:
            return None
        old_status = task.status
        if old_status in ('completed', 'cancelled', 'timeout'):
            return {'task_id': task_id, 'status': task.status, 'message': 'task already finished'}

        now = datetime.now(timezone.utc)
        task.status = 'cancelled'
        
        task.ended_at = now
        log_event_with_session(
            session, tenant_id=tenant_id,
            event_type='scan_task_cancelled',
            reference_id=str(task_id),
            payload={'previous_status': task.status},
        )
        session.commit()
        return {'task_id': task_id, 'status': 'cancelled', 'message': 'task cancelled'}


def check_scan_timeout(
    tenant_id: str,
    timeout_seconds: int = 300,
) -> dict:
    engine = get_engine()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=timeout_seconds)
    timed_out_ids: list[int] = []

    with Session(engine) as session:
        rows = session.execute(
            select(ScanTask)
            .where(ScanTask.tenant_id == tenant_id)
            .where(ScanTask.status.in_(['pending', 'running']))
            .where(ScanTask.created_at < cutoff)
        ).scalars().all()

        for task in rows:
            task.status = 'timeout'
            task.ended_at = now
            timed_out_ids.append(task.task_id)
            log_event_with_session(
                session, tenant_id=tenant_id,
                event_type='scan_task_timeout',
                reference_id=str(task.task_id),
                payload={'previous_status': task.status, 'timeout_seconds': timeout_seconds},
            )

        session.commit()

    return {
        'tenant_id': tenant_id,
        'timeout_seconds': timeout_seconds,
        'timed_out_count': len(timed_out_ids),
        'timed_out_task_ids': timed_out_ids,
    }




