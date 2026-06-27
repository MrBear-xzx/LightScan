import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.policy import Policy
from app.schemas.scan_policy import (
    ScanPolicyCreate,
    ScanPolicyListResponse,
    ScanPolicyResponse,
    ScanPolicyRule,
)


_POLICY_NAME_PREFIX = 'scan_template_'


def list_scan_policies(tenant_id: str) -> ScanPolicyListResponse:
    engine = get_engine()
    with Session(engine) as session:
        rows = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.name.like(_POLICY_NAME_PREFIX + '%'))
            .order_by(Policy.policy_id.desc())
        ).scalars().all()
        items = [_policy_row_to_response(row) for row in rows]
        return ScanPolicyListResponse(tenant_id=tenant_id, total=len(items), items=items)


def get_scan_policy(tenant_id: str, name: str) -> ScanPolicyResponse | None:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.name == _POLICY_NAME_PREFIX + name)
            .order_by(Policy.policy_id.desc())
            .limit(1)
        ).scalar_one_or_none()
        if row is None:
            return None
        return _policy_row_to_response(row)


def upsert_scan_policy(tenant_id: str, req: ScanPolicyCreate) -> ScanPolicyResponse:
    engine = get_engine()
    full_name = _POLICY_NAME_PREFIX + req.name
    config = {
        'description': req.description,
        'plugins': [p.model_dump() for p in req.plugins],
        'extra_config': req.extra_config,
    }
    with Session(engine) as session:
        existing = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.name == full_name)
            .order_by(Policy.policy_id.desc())
            .limit(1)
        ).scalar_one_or_none()
        if existing is None:
            row = Policy(
                tenant_id=tenant_id,
                name=full_name,
                config_json=json.dumps(config, ensure_ascii=False),
            )
            session.add(row)
        else:
            existing.config_json = json.dumps(config, ensure_ascii=False)
        session.commit()

    return get_scan_policy(tenant_id, req.name)


def delete_scan_policy(tenant_id: str, name: str) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.name == _POLICY_NAME_PREFIX + name)
            .order_by(Policy.policy_id.desc())
            .limit(1)
        ).scalar_one_or_none()
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True


def _policy_row_to_response(row: Policy) -> ScanPolicyResponse:
    config = json.loads(row.config_json)
    plugins = [ScanPolicyRule(**p) for p in config.get('plugins', [])]
    return ScanPolicyResponse(
        tenant_id=row.tenant_id,
        name=row.name[len(_POLICY_NAME_PREFIX):],
        description=config.get('description', ''),
        plugins=plugins,
        extra_config=config.get('extra_config', {}),
    )
