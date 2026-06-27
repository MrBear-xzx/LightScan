from fastapi import APIRouter, Query

from app.schemas.operation_log import OperationLogResponse
from app.services.operation_log_service import query_operation_logs

router = APIRouter(prefix='/api/v1/ops', tags=['ops'])


@router.get(
    '/logs',
    response_model=OperationLogResponse,
    summary='操作日志查询',
    description='查询平台操作日志（基于 events 表），支持分页与事件类型过滤。',
)
def get_operation_logs(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
    page: int = Query(default=1, ge=1, description='页码'),
    page_size: int = Query(default=20, ge=1, le=100, description='每页条数'),
    event_type: str | None = Query(default=None, min_length=1, description='事件类型过滤'),
) -> OperationLogResponse:
    return query_operation_logs(tenant_id, page, page_size, event_type)
