from datetime import datetime
from uuid import uuid4

from app.db.session import get_engine
from app.schemas.batch_scan import BatchScanRequest, BatchScanResponse, BatchScanTaskItem
from app.services.discovery_service import create_discovery_task_raw
from app.services.event_service import log_event


def _batch_id() -> str:
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')
    return 'batch-' + date_str + '-' + uuid4().hex[:8]


def create_batch_scan(req: BatchScanRequest) -> BatchScanResponse:
    batch_id = _batch_id()
    engine = get_engine()
    tasks: list[BatchScanTaskItem] = []
    errors: list[str] = []
    succeeded = 0

    for idx, batch in enumerate(req.batches):
        try:
            with engine.begin() as conn:
                row = create_discovery_task_raw(
                    conn=conn,
                    tenant_id=req.tenant_id,
                    targets=batch.targets,
                    policy_id=batch.policy_id,
                )
            tasks.append(
                BatchScanTaskItem(
                    task_id=row['task_id'],
                    tenant_id=row['tenant_id'],
                    targets=batch.targets,
                    policy_id=batch.policy_id,
                    status=row['status'],
                )
            )
            succeeded += 1
        except Exception as exc:
            errors.append('batch[' + str(idx) + '] targets=' + str(batch.targets) + ': ' + str(exc))

    with engine.begin() as conn:
        log_event(
            conn=conn,
            tenant_id=req.tenant_id,
            event_type='batch_scan_created',
            reference_id=batch_id,
            payload={
                'batch_id': batch_id,
                'total': len(req.batches),
                'succeeded': succeeded,
                'task_ids': [t.task_id for t in tasks],
                'failed': len(req.batches) - succeeded,
            },
        )

    return BatchScanResponse(
        batch_id=batch_id,
        tenant_id=req.tenant_id,
        total=len(req.batches),
        succeeded=succeeded,
        failed=len(req.batches) - succeeded,
        tasks=tasks,
        errors=errors,
    )


