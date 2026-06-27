from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectMemberAdd,
    ProjectMemberResponse,
    ProjectResponse,
)
from app.services.project_service import (
    add_member,
    create_project,
    delete_project,
    list_members,
    list_projects,
)

router = APIRouter(prefix='/api/v1/projects', tags=['projects'])


@router.get('', response_model=ProjectListResponse)
def get_projects(
    tenant_id: str = Query(default='default', min_length=1),
) -> ProjectListResponse:
    return list_projects(tenant_id)


@router.post('', response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def post_project(payload: ProjectCreate) -> ProjectResponse:
    return create_project(payload)


@router.delete('/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_project(
    project_id: int,
    tenant_id: str = Query(default='default', min_length=1),
) -> None:
    deleted = delete_project(tenant_id, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='project not found')


@router.get('/{project_id}/members', response_model=list[ProjectMemberResponse])
def get_members(
    project_id: int,
    tenant_id: str = Query(default='default', min_length=1),
) -> list[ProjectMemberResponse]:
    return list_members(tenant_id, project_id)


@router.post('/{project_id}/members', response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def post_member(
    project_id: int,
    payload: ProjectMemberAdd,
    tenant_id: str = Query(default='default', min_length=1),
) -> ProjectMemberResponse:
    return add_member(tenant_id, project_id, payload)
