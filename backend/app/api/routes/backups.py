from fastapi import APIRouter, Query, status

from app.schemas.backup import BackupCreateResponse, BackupListResponse
from app.services.backup_service import create_backup, list_backups

router = APIRouter(prefix='/api/v1/ops/backups', tags=['ops'])


@router.get(
    '',
    response_model=BackupListResponse,
    summary='备份列表',
    description='查询备份记录列表。',
)
def get_backups(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> BackupListResponse:
    return list_backups(tenant_id)


@router.post(
    '',
    response_model=BackupCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary='创建备份',
    description='触发数据库备份（当前为记录占位，实际备份需集成外部工具）。',
)
def post_backup(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
    description: str = Query(default='', description='备份描述'),
) -> BackupCreateResponse:
    return create_backup(tenant_id, description)
