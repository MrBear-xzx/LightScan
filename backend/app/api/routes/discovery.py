from fastapi import APIRouter, status

from app.schemas.discovery import DiscoveryTaskCreate, DiscoveryTaskResponse
from app.services.discovery_service import create_discovery_task

router = APIRouter(prefix='/api/v1/discovery', tags=['discovery'])


@router.post(
    '/tasks',
    response_model=DiscoveryTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary='创建发现任务',
    description=(
        '创建一个资产发现任务。\n'
        '- tenant_id: 租户标识\n'
        '- targets: 目标列表（域名/IP）\n'
        '- policy_id: 策略标识'
    ),
    response_description='任务创建结果（pending）',
)
def create_task(payload: DiscoveryTaskCreate) -> DiscoveryTaskResponse:
    task = create_discovery_task(payload)
    return DiscoveryTaskResponse(
        task_id=task.task_id,
        tenant_id=task.tenant_id,
        task_type=task.task_type,
        status=task.status,
    )
