from fastapi import Header


def require_tenant_guard() -> str:
    """Always return default tenant — no multi-tenant auth in this version."""
    return 'default'


def validate_tenant_guard(tenant_id: str, x_tenant_id: str | None) -> str:
    """No-op: always return default tenant."""
    return 'default'
