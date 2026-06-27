from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.rbac import get_current_user_payload, require_permission, require_role

router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


class PermissionCheckResponse(BaseModel):
    user_id: int
    username: str
    role: str
    permissions: list[str]


@router.get('/permissions', response_model=PermissionCheckResponse)
def get_permissions(
    payload: dict = Depends(get_current_user_payload),
) -> PermissionCheckResponse:
    # Return all permissions the user's role satisfies
    from app.auth.rbac import PERMISSIONS, ROLE_HIERARCHY
    role = payload.get('role', 'viewer')
    user_level = ROLE_HIERARCHY.get(role, 0)
    granted = [perm for perm, level in PERMISSIONS.items() if user_level >= level]
    return PermissionCheckResponse(
        user_id=int(payload['sub']),
        username=payload['username'],
        role=role,
        permissions=granted,
    )


# Protected endpoints for testing RBAC
@router.get('/admin-only')
def admin_only(payload: dict = Depends(require_role('admin'))) -> dict:
    return {'message': 'admin access granted', 'user': payload['username']}


@router.get('/analyst-or-above')
def analyst_or_above(payload: dict = Depends(require_role('analyst'))) -> dict:
    return {'message': 'analyst+ access granted', 'user': payload['username']}


@router.get('/vuln-write')
def vuln_write(payload: dict = Depends(require_permission('vuln:write'))) -> dict:
    return {'message': 'vuln:write granted', 'user': payload['username']}
