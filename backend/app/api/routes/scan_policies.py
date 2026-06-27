from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.scan_policy import (
    ScanPolicyCreate,
    ScanPolicyListResponse,
    ScanPolicyResponse,
)
from app.services.scan_policy_service import (
    delete_scan_policy,
    get_scan_policy,
    list_scan_policies,
    upsert_scan_policy,
)

router = APIRouter(prefix='/api/v1/scan/policies', tags=['scan'])


@router.get(
    '',
    response_model=ScanPolicyListResponse,
    summary='扫描策略模板列表',
)
def list_policies(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> ScanPolicyListResponse:
    return list_scan_policies(tenant_id)


@router.get(
    '/{name}',
    response_model=ScanPolicyResponse,
    summary='获取扫描策略模板详情',
)
def get_policy(
    name: str,
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> ScanPolicyResponse:
    result = get_scan_policy(tenant_id, name)
    if result is None:
        raise HTTPException(status_code=404, detail='policy not found')
    return result


@router.put(
    '',
    response_model=ScanPolicyResponse,
    status_code=status.HTTP_200_OK,
    summary='创建或更新扫描策略模板',
)
def put_policy(payload: ScanPolicyCreate) -> ScanPolicyResponse:
    return upsert_scan_policy(payload.tenant_id, payload)


@router.delete(
    '/{name}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='删除扫描策略模板',
)
def delete_policy(
    name: str,
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> None:
    deleted = delete_scan_policy(tenant_id, name)
    if not deleted:
        raise HTTPException(status_code=404, detail='policy not found')
