from app.plugins.registry import build_default_registry


def test_build_default_registry_supports_tenant_rollout() -> None:
    registry = build_default_registry(tenant_id='t1')
    items = registry.list_plugins()
    assert len(items) >= 3
