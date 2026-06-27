from fastapi import APIRouter, HTTPException, Query
from app.db.session import get_engine
from app.models.scan_task import ScanTask
from sqlalchemy import select
from sqlalchemy.orm import Session
import json as _j

router = APIRouter(prefix='/api/v1/scan', tags=['scan'])


@router.get(
    '/tasks/{task_id}',
    summary='获取扫描任务详情',
    description='返回任务基本信息和检查结果',
)
def scan_task_detail(
    task_id: int,
    tenant_id: str = Query(default='default', min_length=1),
) -> dict:
    engine = get_engine()
    with Session(engine) as session:
        t = session.execute(
            select(ScanTask).where(ScanTask.task_id == task_id, ScanTask.tenant_id == tenant_id)
        ).scalar_one_or_none()
        if t is None:
            raise HTTPException(status_code=404, detail='任务不存在')
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
