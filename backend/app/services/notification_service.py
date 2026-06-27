import json
import urllib.request
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.policy import Policy
from app.models.vuln_case import VulnCase
from app.services.event_service import log_event_with_session
from app.services.notification_adapters import ADAPTER_BUILDERS


def preview_notifications(session: Session, tenant_id: str, min_risk_score: float) -> list[VulnCase]:
    return session.execute(
        select(VulnCase)
        .where(VulnCase.tenant_id == tenant_id)
        .where(VulnCase.risk_score >= min_risk_score)
        .where(VulnCase.state.in_(['new', 'confirmed', 'reopened']))
        .order_by(VulnCase.risk_score.desc())
        .limit(100)
    ).scalars().all()


def _send_json_post(webhook_url: str, payload: dict) -> bool:
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        webhook_url,
        data=body,
        method='POST',
        headers={'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False



def _build_provider_payload(provider: str, tenant_id: str, base_payload: dict) -> dict:
    builder = ADAPTER_BUILDERS.get(provider)
    if builder is None:
        return {'tenant_id': tenant_id, **base_payload}
    return builder(tenant_id, base_payload)


def _has_recent_dispatch(
    session: Session,
    tenant_id: str,
    case_id: int,
    dedup_window_minutes: int,
) -> bool:
    if dedup_window_minutes <= 0:
        return False
    threshold = datetime.now(timezone.utc) - timedelta(minutes=dedup_window_minutes)
    event = session.execute(
        select(Event.event_id)
        .where(Event.tenant_id == tenant_id)
        .where(Event.event_type == 'notification_dispatched')
        .where(Event.reference_id == str(case_id))
        .where(Event.created_at >= threshold)
        .order_by(Event.event_id.desc())
        .limit(1)
    ).scalar_one_or_none()
    return event is not None


def _resolve_dedup_window_for_case(
    risk_score: float,
    dedup_window_minutes: int,
    dedup_policy_by_risk: dict[str, int] | None,
) -> int:
    if not dedup_policy_by_risk:
        return dedup_window_minutes

    if risk_score >= 8.0:
        return int(dedup_policy_by_risk.get('high', dedup_window_minutes))
    if risk_score >= 5.0:
        return int(dedup_policy_by_risk.get('medium', dedup_window_minutes))
    return int(dedup_policy_by_risk.get('low', dedup_window_minutes))


def dispatch_notifications(
    session: Session,
    tenant_id: str,
    min_risk_score: float,
    provider: str = 'webhook',
    webhook_url: str | None = None,
    dedup_window_minutes: int = 30,
    dedup_policy_by_risk: dict[str, int] | None = None,
) -> tuple[int, int, int, int]:
    rows = preview_notifications(session, tenant_id, min_risk_score)
    dispatched = 0
    suppressed = 0
    sent = 0
    failed = 0

    for row in rows:
        case_dedup_window = _resolve_dedup_window_for_case(
            row.risk_score,
            dedup_window_minutes,
            dedup_policy_by_risk,
        )
        if _has_recent_dispatch(session, tenant_id, row.case_id, case_dedup_window):
            suppressed += 1
            log_event_with_session(
                session,
                tenant_id=tenant_id,
                event_type='notification_suppressed',
                reference_id=str(row.case_id),
                payload={
                    'case_id': row.case_id,
                    'dedup_window_minutes': case_dedup_window,
                },
            )
            continue

        base_payload = {
            'case_id': row.case_id,
            'risk_score': row.risk_score,
            'state': row.state,
            'owner': row.owner,
        }
        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type='notification_dispatched',
            reference_id=str(row.case_id),
            payload=base_payload,
        )
        dispatched += 1

        if webhook_url:
            provider_payload = _build_provider_payload(provider, tenant_id, base_payload)
            ok = _send_json_post(webhook_url, provider_payload)
            if ok:
                sent += 1
                log_event_with_session(
                    session,
                    tenant_id=tenant_id,
                    event_type=f'notification_{provider}_sent',
                    reference_id=str(row.case_id),
                    payload={'webhook_url': webhook_url, **base_payload},
                )
            else:
                failed += 1
                log_event_with_session(
                    session,
                    tenant_id=tenant_id,
                    event_type=f'notification_{provider}_failed',
                    reference_id=str(row.case_id),
                    payload={'webhook_url': webhook_url, **base_payload},
                )

    session.commit()

    if not webhook_url:
        sent = dispatched
        failed = 0

    return dispatched, suppressed, sent, failed


def get_notification_policy(session: Session, tenant_id: str) -> dict | None:
    policy = session.execute(
        select(Policy)
        .where(Policy.tenant_id == tenant_id)
        .where(Policy.name == 'notification')
        .order_by(Policy.policy_id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if policy is None:
        return None
    return json.loads(policy.config_json)


def upsert_notification_policy(
    session: Session,
    tenant_id: str,
    dedup_window_minutes: int,
    dedup_policy_by_risk: dict[str, int] | None,
) -> dict:
    config = {
        'dedup_window_minutes': dedup_window_minutes,
        'dedup_policy_by_risk': dedup_policy_by_risk,
    }
    existing = session.execute(
        select(Policy)
        .where(Policy.tenant_id == tenant_id)
        .where(Policy.name == 'notification')
        .order_by(Policy.policy_id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if existing is None:
        row = Policy(
            tenant_id=tenant_id,
            name='notification',
            config_json=json.dumps(config, ensure_ascii=False),
        )
        session.add(row)
    else:
        existing.config_json = json.dumps(config, ensure_ascii=False)
    session.commit()
    return config



