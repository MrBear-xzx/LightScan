from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.services.plugin_rollout_service import get_plugin_rollout_policy


def get_plugin_rollout(plugin_id: str, tenant_id: str = 'default') -> dict[str, str]:
    engine = get_engine()
    with Session(engine) as session:
        policy = get_plugin_rollout_policy(session, tenant_id)
    return policy.get(plugin_id, {'status': 'enabled', 'rollout': 'stable'})
