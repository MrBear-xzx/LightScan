import json
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.tenant_guard import require_tenant_guard, validate_tenant_guard
from app.db.session import get_engine
from app.plugins.registry import build_default_registry
from app.schemas.plugin import (
    PluginRolloutAuditItem,
    PluginRolloutAuditResponse,
    PluginRolloutPolicyDiffItem,
    PluginRolloutPolicyResponse,
    PluginRolloutPolicyUpsertRequest,
    PluginRolloutPolicyUpsertResponse,
)
from app.services.event_service import log_event_with_session
from app.services.plugin_rollout_service import (
    ALLOWED_PLUGIN_IDS,
    count_plugin_rollout_audit_events,
    get_plugin_rollout_policy,
    list_plugin_rollout_audit_events,
    upsert_plugin_rollout_policy,
)

router = APIRouter(prefix='/api/v1/plugins', tags=['plugins'])


@router.get('', summary='查询插件列表')
def list_plugins(
    tenant_id: str = Query(default='default', min_length=1),
    capability: str | None = Query(default=None, min_length=1),
    status: str | None = Query(default=None, pattern='^(enabled|disabled)$'),
) -> dict:
    registry = build_default_registry(tenant_id=tenant_id)
    items = registry.list_plugins(capability=capability, status=status)
    return {
        'total': len(items),
        'items': [
            {
                'plugin_id': item.plugin_id,
                'kind': item.kind,
                'version': item.version,
                'capabilities': item.capabilities,
                'status': item.status,
                'rollout': item.rollout,
            }
            for item in items
        ],
    }


@router.get('/health', summary='查询插件健康状态')
def plugins_health(
    tenant_id: str = Query(default='default', min_length=1),
) -> dict:
    registry = build_default_registry(tenant_id=tenant_id)
    plugin_items = registry.list_plugins(status='enabled')

    items: list[dict] = []
    healthy = 0
    for item in plugin_items:
        health = item.plugin.health()
        plugin_status = str(health.get('status', 'unknown'))
        if plugin_status == 'healthy':
            healthy += 1
        items.append(
            {
                'plugin_id': item.plugin_id,
                'kind': item.kind,
                'status': plugin_status,
            }
        )

    total = len(plugin_items)
    return {
        'total': total,
        'healthy': healthy,
        'items': items,
    }


@router.get('/rollout-policy', response_model=PluginRolloutPolicyResponse, summary='查询插件 rollout 策略')
def get_rollout_policy(
    tenant_id: str = Depends(require_tenant_guard),
) -> PluginRolloutPolicyResponse:
    engine = get_engine()
    with Session(engine) as session:
        plugins = get_plugin_rollout_policy(session, tenant_id)
    return PluginRolloutPolicyResponse(tenant_id=tenant_id, plugins=plugins)


@router.put('/rollout-policy', response_model=PluginRolloutPolicyUpsertResponse, summary='设置插件 rollout 策略')
def put_rollout_policy(
    payload: PluginRolloutPolicyUpsertRequest,
    x_tenant_id: str | None = Header(default=None, alias='X-Tenant-ID'),
) -> PluginRolloutPolicyUpsertResponse:
    tenant_id = validate_tenant_guard(payload.tenant_id, x_tenant_id)
    if any(plugin_id not in ALLOWED_PLUGIN_IDS for plugin_id in payload.plugins.keys()):
        raise HTTPException(status_code=400, detail='unknown plugin in rollout policy')

    plugins_payload = {plugin_id: rule.model_dump() for plugin_id, rule in payload.plugins.items()}
    engine = get_engine()
    with Session(engine) as session:
        previous_plugins = get_plugin_rollout_policy(session, tenant_id=tenant_id)
        plugins = upsert_plugin_rollout_policy(session, tenant_id=tenant_id, plugins=plugins_payload)
        diff: dict[str, PluginRolloutPolicyDiffItem] = {}
        plugin_ids = set(previous_plugins.keys()) | set(plugins.keys())
        for plugin_id in plugin_ids:
            before = previous_plugins.get(plugin_id)
            after = plugins.get(plugin_id)
            if before == after:
                continue
            diff[plugin_id] = PluginRolloutPolicyDiffItem(before=before, after=after)
        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type='plugin_rollout_policy_updated',
            reference_id=tenant_id,
            payload={'plugins': plugins, 'diff': {plugin_id: item.model_dump() for plugin_id, item in diff.items()}},
        )
        session.commit()
    return PluginRolloutPolicyUpsertResponse(tenant_id=tenant_id, plugins=plugins, diff=diff)


@router.get('/rollout-audit', response_model=PluginRolloutAuditResponse, summary='查询插件 rollout 审计事件')
def get_rollout_audit(
    tenant_id: str = Depends(require_tenant_guard),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    event_type: str | None = Query(default=None, min_length=1),
    plugin_id: str | None = Query(default=None, min_length=1),
    requested_from: datetime | None = Query(default=None),
    requested_to: datetime | None = Query(default=None),
) -> PluginRolloutAuditResponse:
    if requested_from and requested_to and requested_from > requested_to:
        raise HTTPException(status_code=400, detail='requested_from must be earlier than requested_to')

    engine = get_engine()
    with Session(engine) as session:
        total = count_plugin_rollout_audit_events(
            session,
            tenant_id,
            event_type,
            plugin_id,
            requested_from,
            requested_to,
        )
        rows = list_plugin_rollout_audit_events(
            session,
            tenant_id,
            page,
            page_size,
            event_type,
            plugin_id,
            requested_from,
            requested_to,
        )

    items = [
        PluginRolloutAuditItem(
            event_id=row.event_id,
            event_type=row.event_type,
            created_at=row.created_at.isoformat(),
            payload=json.loads(row.payload_json),
        )
        for row in rows
    ]
    return PluginRolloutAuditResponse(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        total=total,
        items=items,
    )
