import json
from datetime import timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.event import Event
from app.models.scan_task import ScanTask
from app.schemas.progress import BatchProgressResponse, ScanTaskProgressItem


def query_scan_progress(
    tenant_id: str,
    batch_id: str | None = None,
    task_ids: list[int] | None = None,
) -> BatchProgressResponse:
    engine = get_engine()
    with Session(engine) as session:
        resolved_task_ids: list[int] = []

        if task_ids:
            resolved_task_ids = task_ids
        elif batch_id:
            event = session.execute(
                select(Event)
                .where(Event.tenant_id == tenant_id)
                .where(Event.event_type == 'batch_scan_created')
                .where(Event.reference_id == batch_id)
                .order_by(Event.event_id.desc())
                .limit(1)
            ).scalar_one_or_none()
            if event is not None:
                payload = json.loads(event.payload_json)
                resolved_task_ids = payload.get('task_ids', [])
            if not resolved_task_ids:
                return BatchProgressResponse(
                    tenant_id=tenant_id, batch_id=batch_id,
                    total=0, completed=0, failed=0, running=0, pending=0, tasks=[],
                )

        # Build query
        stmt = select(ScanTask).where(ScanTask.tenant_id == tenant_id)
        if resolved_task_ids:
            stmt = stmt.where(ScanTask.task_id.in_(resolved_task_ids))
        stmt = stmt.order_by(ScanTask.task_id.desc())
        if not resolved_task_ids:
            stmt = stmt.limit(50)

        rows = session.execute(stmt).scalars().all()

        tasks = []
        completed = failed = running = pending = 0
        for row in rows:
            status = row.status
            if status == 'completed':
                completed += 1
            elif status == 'failed':
                failed += 1
            elif status == 'running':
                running += 1
            else:
                pending += 1
            target_list = json.loads(row.target_scope) if isinstance(row.target_scope, str) else (row.target_scope or [])
            target_str = ", ".join(target_list[:3]) if target_list else ""
            tasks.append(ScanTaskProgressItem(
                task_id=row.task_id,
                target=target_str,
                task_type=row.task_type,
                status=row.status,
                error_message=row.error_message,
                result_summary=row.result_summary,
                worker_id=row.worker_id,
                started_at=row.started_at.isoformat() if row.started_at and row.started_at.tzinfo else (row.started_at.replace(tzinfo=timezone.utc).isoformat() if row.started_at else None),
                ended_at=row.ended_at.isoformat() if row.ended_at and row.ended_at.tzinfo else (row.ended_at.replace(tzinfo=timezone.utc).isoformat() if row.ended_at else None),
            ))

        return BatchProgressResponse(
            tenant_id=tenant_id,
            batch_id=batch_id,
            total=len(tasks),
            completed=completed,
            failed=failed,
            running=running,
            pending=pending,
            tasks=tasks,
        )
