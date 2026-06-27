import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.policy import Policy
from app.schemas.webhook_subscription import (
    WebhookSubscription,
    WebhookSubscriptionListResponse,
    WebhookSubscriptionResponse,
)

_SUB_PREFIX = 'webhook_sub_'


def list_subscriptions(tenant_id: str) -> WebhookSubscriptionListResponse:
    engine = get_engine()
    with Session(engine) as session:
        rows = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.name.like(_SUB_PREFIX + '%'))
            .order_by(Policy.policy_id.desc())
        ).scalars().all()
        items = [_row_to_response(r) for r in rows]
        return WebhookSubscriptionListResponse(tenant_id=tenant_id, total=len(items), items=items)


def create_subscription(tenant_id: str, config: WebhookSubscription) -> WebhookSubscriptionResponse:
    engine = get_engine()
    full_name = _SUB_PREFIX + config.url[:32]
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


def delete_subscription(tenant_id: str, sub_id: int) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.policy_id == sub_id)
            .where(Policy.name.like(_SUB_PREFIX + '%'))
        ).scalar_one_or_none()
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True


def _row_to_response(row: Policy) -> WebhookSubscriptionResponse:
    config = WebhookSubscription(**json.loads(row.config_json))
    return WebhookSubscriptionResponse(sub_id=row.policy_id, tenant_id=row.tenant_id, config=config)
