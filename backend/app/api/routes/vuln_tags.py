from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.vuln_tag import (
    VulnTagCreate,
    VulnTagListResponse,
    VulnTagResponse,
    VulnCaseTagAssignRequest,
)
from app.services.vuln_tag_service import (
    assign_tags_to_case,
    create_tag,
    delete_tag,
    get_tags_for_case,
    list_tags,
)

router = APIRouter(prefix='/api/v1/vuln-cases', tags=['vuln-cases'])


@router.get(
    '/tags',
    response_model=VulnTagListResponse,
    summary='标签列表',
)
def get_tag_list(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> VulnTagListResponse:
    return list_tags(tenant_id)


@router.post(
    '/tags',
    response_model=VulnTagResponse,
    status_code=status.HTTP_201_CREATED,
    summary='创建标签',
)
def post_tag(payload: VulnTagCreate) -> VulnTagResponse:
    return create_tag(payload)


@router.delete(
    '/tags/{tag_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='删除标签',
)
def remove_tag(
    tag_id: int,
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> None:
    deleted = delete_tag(tenant_id, tag_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='?????')


@router.post(
    '/{case_id}/tags',
    summary='给漏洞案例分配标签',
)
def assign_tags(
    case_id: int,
    payload: VulnCaseTagAssignRequest,
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> dict:
    result = assign_tags_to_case(tenant_id, payload)
    if not result['success']:
        raise HTTPException(status_code=404, detail=result['message'])
    return result


@router.get(
    '/{case_id}/tags',
    response_model=list[VulnTagResponse],
    summary='查询漏洞案例的标签',
)
def get_case_tags(
    case_id: int,
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> list[VulnTagResponse]:
    return get_tags_for_case(tenant_id, case_id)
