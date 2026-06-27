from fastapi import Depends, HTTPException, Header

from app.auth.jwt import decode_access_token

# Role hierarchy: admin > analyst > viewer
ROLE_HIERARCHY = {
    'admin': 100,
    'analyst': 50,
    'viewer': 10,
}

# Permission definitions
PERMISSIONS: dict[str, int] = {
    # vuln-cases
    'vuln:read': 10,
    'vuln:write': 50,
    'vuln:delete': 100,
    'vuln:assign': 50,
    # scan
    'scan:read': 10,
    'scan:write': 50,
    'scan:cancel': 50,
    'scan:manage': 100,
    # risk
    'risk:read': 10,
    'risk:write': 50,
    # ops
    'ops:read': 10,
    'ops:write': 50,
    'ops:admin': 100,
    # admin
    'admin:all': 100,
}


def get_current_user_payload(authorization: str | None = Header(default=None)) -> dict:
    """Extract and validate JWT from Authorization header."""
    if authorization is None:
        raise HTTPException(status_code=401, detail='??????')
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer':
        raise HTTPException(status_code=401, detail='??????')
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail='????????')
    return payload


def require_permission(permission: str):
    """Dependency factory: checks if current user has required permission level."""
    required_level = PERMISSIONS.get(permission)
    if required_level is None:
        raise ValueError(f'unknown permission: {permission}')

    def _checker(payload: dict = Depends(get_current_user_payload)) -> dict:
        role = payload.get('role', 'viewer')
        user_level = ROLE_HIERARCHY.get(role, 0)
        if user_level < required_level:
            raise HTTPException(
                status_code=403,
                detail=f'insufficient permissions: required {permission}, role={role}',
            )
        return payload

    return _checker


def require_role(min_role: str):
    """Dependency factory: checks minimum role level."""
    min_level = ROLE_HIERARCHY.get(min_role, 0)

    def _checker(payload: dict = Depends(get_current_user_payload)) -> dict:
        role = payload.get('role', 'viewer')
        user_level = ROLE_HIERARCHY.get(role, 0)
        if user_level < min_level:
            raise HTTPException(
                status_code=403,
                detail=f'insufficient role: required {min_role}, current {role}',
            )
        return payload

    return _checker
