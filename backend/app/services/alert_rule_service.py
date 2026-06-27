import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.policy import Policy
from app.schemas.alert_rule import (
    AlertRuleConfig,
    AlertRuleListResponse,
    AlertRuleResponse,
)

_ALERT_RULE_PREFIX = 'alert_rule_'


def list_alert_rules(tenant_id: str) -> AlertRuleListResponse:
    engine = get_engine()
    with Session(engine) as session:
        rows = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.name.like(_ALERT_RULE_PREFIX + '%'))
            .order_by(Policy.policy_id.desc())
        ).scalars().all()
        items = [_row_to_response(row) for row in rows]
        return AlertRuleListResponse(tenant_id=tenant_id, total=len(items), items=items)


def get_alert_rule(tenant_id: str, rule_id: int) -> AlertRuleResponse | None:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.policy_id == rule_id)
            .where(Policy.name.like(_ALERT_RULE_PREFIX + '%'))
        ).scalar_one_or_none()
        if row is None:
            return None
        return _row_to_response(row)


def create_alert_rule(tenant_id: str, config: AlertRuleConfig) -> AlertRuleResponse:
    engine = get_engine()
    full_name = _ALERT_RULE_PREFIX + config.name
    with Session(engine) as session:
        row = Policy(
            tenant_id=tenant_id,
            name=full_name,
            config_json=json.dumps(config.model_dump(), ensure_ascii=False),
        )
        session.add(row)
        session.commit()
        session.refresh(row)
    return _row_to_response(row)


def delete_alert_rule(tenant_id: str, rule_id: int) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.policy_id == rule_id)
            .where(Policy.name.like(_ALERT_RULE_PREFIX + '%'))
        ).scalar_one_or_none()
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True


def _row_to_response(row: Policy) -> AlertRuleResponse:
    config = AlertRuleConfig(**json.loads(row.config_json))
    return AlertRuleResponse(
        rule_id=row.policy_id,
        tenant_id=row.tenant_id,
        config=config,
    )
