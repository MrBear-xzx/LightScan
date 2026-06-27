import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.policy import Policy
from app.schemas.notification_template import (
    NotificationTemplate,
    NotificationTemplateListResponse,
    NotificationTemplateResponse,
)

_TEMPLATE_PREFIX = 'notify_template_'


def list_templates(tenant_id: str) -> NotificationTemplateListResponse:
    engine = get_engine()
    with Session(engine) as session:
        rows = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.name.like(_TEMPLATE_PREFIX + '%'))
            .order_by(Policy.policy_id.desc())
        ).scalars().all()
        items = [_row_to_response(r) for r in rows]
        return NotificationTemplateListResponse(tenant_id=tenant_id, total=len(items), items=items)


def get_template(tenant_id: str, template_id: int) -> NotificationTemplateResponse | None:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.policy_id == template_id)
            .where(Policy.name.like(_TEMPLATE_PREFIX + '%'))
        ).scalar_one_or_none()
        if row is None:
            return None
        return _row_to_response(row)


def create_template(tenant_id: str, config: NotificationTemplate) -> NotificationTemplateResponse:
    engine = get_engine()
    full_name = _TEMPLATE_PREFIX + config.name
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


def delete_template(tenant_id: str, template_id: int) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.policy_id == template_id)
            .where(Policy.name.like(_TEMPLATE_PREFIX + '%'))
        ).scalar_one_or_none()
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True


def render_template(config: NotificationTemplate, variables: dict) -> tuple[str, str]:
    title = config.title_template
    body = config.body_template
    for key, val in variables.items():
        placeholder = '{' + key + '}'
        title = title.replace(placeholder, str(val))
        body = body.replace(placeholder, str(val))
    return title, body


def _row_to_response(row: Policy) -> NotificationTemplateResponse:
    config = NotificationTemplate(**json.loads(row.config_json))
    return NotificationTemplateResponse(
        template_id=row.policy_id,
        tenant_id=row.tenant_id,
        config=config,
    )
