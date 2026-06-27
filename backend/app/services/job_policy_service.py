import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.policy import Policy

DEFAULT_MAX_RETRY_COUNT = 3
DEFAULT_RETRY_COOLDOWN_SECONDS = 60


def get_job_retry_policy(session: Session, tenant_id: str) -> dict:
    policy = session.execute(
        select(Policy)
        .where(Policy.tenant_id == tenant_id)
        .where(Policy.name == 'jobs_retry')
        .order_by(Policy.policy_id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if policy is None:
        return {
            'max_retry_count': DEFAULT_MAX_RETRY_COUNT,
            'retry_cooldown_seconds': DEFAULT_RETRY_COOLDOWN_SECONDS,
        }
    config = json.loads(policy.config_json)
    return {
        'max_retry_count': int(config.get('max_retry_count', DEFAULT_MAX_RETRY_COUNT)),
        'retry_cooldown_seconds': int(config.get('retry_cooldown_seconds', DEFAULT_RETRY_COOLDOWN_SECONDS)),
    }


def upsert_job_retry_policy(
    session: Session,
    tenant_id: str,
    max_retry_count: int,
    retry_cooldown_seconds: int,
) -> dict:
    config = {
        'max_retry_count': max_retry_count,
        'retry_cooldown_seconds': retry_cooldown_seconds,
    }
    existing = session.execute(
        select(Policy)
        .where(Policy.tenant_id == tenant_id)
        .where(Policy.name == 'jobs_retry')
        .order_by(Policy.policy_id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if existing is None:
        row = Policy(
            tenant_id=tenant_id,
            name='jobs_retry',
            config_json=json.dumps(config, ensure_ascii=False),
        )
        session.add(row)
    else:
        existing.config_json = json.dumps(config, ensure_ascii=False)
    session.commit()
    return config
