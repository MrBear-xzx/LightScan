from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.aggregation import ScanAggregationResponse
from app.schemas.batch_scan import BatchScanRequest, BatchScanResponse
from app.schemas.progress import BatchProgressResponse
from app.services.aggregation_service import query_scan_aggregation
from app.services.batch_scan_service import create_batch_scan
from app.services.progress_service import query_scan_progress
from app.services.task_control_service import cancel_scan_task, check_scan_timeout

router = APIRouter(prefix='/api/v1/scan', tags=['scan'])

@router.get(
    '/tasks/{task_id}',
    summary='????????',
    description='?????????????',
)
def scan_task_detail(
    task_id: int,
    tenant_id: str = Query(default='default', min_length=1),
) -> dict:
    from app.db.session import get_engine
    from app.models.scan_task import ScanTask
    from sqlalchemy import select
    from sqlalchemy.orm import Session
    import json as _j
    engine = get_engine()
    with Session(engine) as session:
        t = session.execute(
            select(ScanTask).where(ScanTask.task_id == task_id, ScanTask.tenant_id == tenant_id)
        ).scalar_one_or_none()
        if t is None:
            raise HTTPException(status_code=404, detail='?????')
        target_list = _j.loads(t.target_scope) if t.target_scope else []
        checks = _j.loads(t.result_summary) if t.result_summary else []
        return {
            'task_id': t.task_id,
            'tenant_id': t.tenant_id,
            'target': ', '.join(target_list[:3]) if target_list else '',
            'status': t.status,
            'started_at': t.started_at.isoformat() if t.started_at else None,
            'ended_at': t.ended_at.isoformat() if t.ended_at else None,
            'check_results': checks,
        }



@router.post(
    '/batch',
    response_model=BatchScanResponse,
    status_code=status.HTTP_200_OK,
    summary='批量扫描',
    description=(
        '一次性提交多个扫描目标组，每个目标组独立创建发现任务。\n'
        '- tenant_id: 租户标识\n'
        '- batches: 批量扫描请求列表，每个元素包含 targets（目标列表）和 policy_id（策略标识）\n'
        '- 返回批次ID与各任务状态'
    ),
)
def batch_scan(payload: BatchScanRequest) -> BatchScanResponse:
    return create_batch_scan(payload)


@router.get(
    '/aggregation',
    response_model=ScanAggregationResponse,
    summary='扫描结果聚合',
    description='按资产维度聚合扫描发现结果，返回严重等级分布与插件分布统计。',
)
def scan_aggregation(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> ScanAggregationResponse:
    return query_scan_aggregation(tenant_id)


@router.get(
    '/progress',
    response_model=BatchProgressResponse,
    summary='扫描任务进度查询',
    description='按批次ID或任务ID列表查询扫描任务执行进度。支持 batch_id（批次ID）或 task_ids（逗号分隔的任务ID列表）。',
)
def scan_progress(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
    batch_id: str | None = Query(default=None, min_length=1, description='批次ID'),
    task_ids: str | None = Query(default=None, description='任务ID列表（逗号分隔）'),
) -> BatchProgressResponse:
    parsed_task_ids: list[int] = []
    if task_ids:
        for tid in task_ids.split(','):
            tid_stripped = tid.strip()
            if tid_stripped.isdigit():
                parsed_task_ids.append(int(tid_stripped))
    return query_scan_progress(
        tenant_id=tenant_id,
        batch_id=batch_id,
        task_ids=parsed_task_ids if parsed_task_ids else None,
    )


@router.post(
    '/{task_id}/cancel',
    summary='取消扫描任务',
    description='将指定扫描任务标记为取消。已完成的、已取消或已超时的任务不可再取消。',
)
def scan_cancel(
    task_id: int,
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> dict:
    result = cancel_scan_task(tenant_id=tenant_id, task_id=task_id)
    if result is None:
        raise HTTPException(status_code=404, detail='?????')
    return result


@router.post(
    '/timeout-check',
    summary='超时任务检测',
    description='检查并标记超时扫描任务。默认300秒内未完成的任务标记为 timeout。',
)
def scan_timeout_check(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
    timeout_seconds: int = Query(default=300, ge=30, description='超时阈值（秒）'),
) -> dict:
    return check_scan_timeout(tenant_id=tenant_id, timeout_seconds=timeout_seconds)
