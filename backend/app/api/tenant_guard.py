from fastapi import Header, HTTPException


def require_tenant_guard(
    tenant_id: str,
    x_tenant_id: str | None = Header(default=None, alias='X-Tenant-ID'),
) -> str:
    if x_tenant_id is None:
        return tenant_id
    if x_tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail='tenant header mismatch')
    return tenant_id


def validate_tenant_guard(tenant_id: str, x_tenant_id: str | None) -> str:
    if x_tenant_id is None:
        return tenant_id
    if x_tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail='tenant header mismatch')
    return tenant_id
