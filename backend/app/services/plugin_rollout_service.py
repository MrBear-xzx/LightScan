import json
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.policy import Policy

DEFAULT_PLUGIN_ROLLOUT_POLICY: dict[str, dict[str, str]] = {
    'http_probe': {'status': 'enabled', 'rollout': 'stable'},
    'nuclei_json': {'status': 'disabled', 'rollout': 'canary'},
    'mockx_json': {'status': 'enabled', 'rollout': 'canary'},
}
ALLOWED_PLUGIN_IDS = set(DEFAULT_PLUGIN_ROLLOUT_POLICY.keys())


def get_plugin_rollout_policy(session: Session, tenant_id: str) -> dict[str, dict[str, str]]:
    policy = session.execute(
        select(Policy)
        .where(Policy.tenant_id == tenant_id)
        .where(Policy.name == 'plugin_rollout')
        .order_by(Policy.policy_id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if policy is None:
        return DEFAULT_PLUGIN_ROLLOUT_POLICY
    config = json.loads(policy.config_json)
    return config.get('plugins', DEFAULT_PLUGIN_ROLLOUT_POLICY)


def upsert_plugin_rollout_policy(
    session: Session,
    tenant_id: str,
    plugins: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    config = {'plugins': plugins}
    existing = session.execute(
        select(Policy)
        .where(Policy.tenant_id == tenant_id)
        .where(Policy.name == 'plugin_rollout')
        .order_by(Policy.policy_id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if existing is None:
        row = Policy(
            tenant_id=tenant_id,
            name='plugin_rollout',
            config_json=json.dumps(config, ensure_ascii=False),
        )
        session.add(row)
    else:
        existing.config_json = json.dumps(config, ensure_ascii=False)
    return plugins


def _build_rollout_audit_query(
    tenant_id: str,
    event_type: str | None = None,
    plugin_id: str | None = None,
    requested_from: datetime | None = None,
    requested_to: datetime | None = None,
):
    query = select(Event).where(Event.tenant_id == tenant_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
    else:
        query = query.where(Event.event_type == 'plugin_rollout_policy_updated')
    if plugin_id:
        query = query.where(Event.payload_json.like(f'%\"{plugin_id}\"%'))
    if requested_from:
        query = query.where(Event.created_at >= requested_from)
    if requested_to:
        query = query.where(Event.created_at <= requested_to)
    return query


def count_plugin_rollout_audit_events(
    session: Session,
    tenant_id: str,
    event_type: str | None = None,
    plugin_id: str | None = None,
    requested_from: datetime | None = None,
    requested_to: datetime | None = None,
) -> int:
    query = _build_rollout_audit_query(tenant_id, event_type, plugin_id, requested_from, requested_to)
    return int(session.execute(select(func.count()).select_from(query.subquery())).scalar_one())


def list_plugin_rollout_audit_events(
    session: Session,
    tenant_id: str,
    page: int,
    page_size: int,
    event_type: str | None = None,
    plugin_id: str | None = None,
    requested_from: datetime | None = None,
    requested_to: datetime | None = None,
) -> list[Event]:
    offset = (page - 1) * page_size
    query = _build_rollout_audit_query(tenant_id, event_type, plugin_id, requested_from, requested_to)
    return session.execute(query.order_by(Event.event_id.desc()).offset(offset).limit(page_size)).scalars().all()
