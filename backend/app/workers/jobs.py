import json

from app.db.session import get_session
from app.plugins.discovery.http_probe import HttpProbeDiscoveryPlugin
from app.plugins.scanner.nuclei_json import NucleiJsonScannerPlugin
from app.services.event_service import log_event_with_session
from app.services.notification_service import dispatch_notifications
from app.services.ticket_service import sync_tickets
from app.workers.celery_app import celery_app


def _task_reference_id(task) -> str:
    request = getattr(task, 'request', None)
    task_id = getattr(request, 'id', None)
    if task_id:
        return str(task_id)
    return 'unknown'


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def run_discovery_task_payload(self, target_scope: str, policy: dict) -> list[dict]:
    plugin = HttpProbeDiscoveryPlugin()
    targets = json.loads(target_scope)
    return plugin.discover(targets, policy)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def run_scan_and_normalize(self, raw_results: list[dict]) -> list[dict]:
    plugin = NucleiJsonScannerPlugin()
    return [plugin.normalize(item) for item in raw_results]


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def dispatch_notification_job(
    self,
    tenant_id: str,
    min_risk_score: float,
    provider: str,
    webhook_url: str | None,
    dedup_window_minutes: int = 30,
    dedup_policy_by_risk: dict[str, int] | None = None,
) -> dict:
    session = get_session()
    try:
        dispatched, suppressed, sent, failed = dispatch_notifications(
            session,
            tenant_id,
            min_risk_score,
            provider,
            webhook_url,
            dedup_window_minutes,
            dedup_policy_by_risk,
        )
        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type='notification_async_finished',
            reference_id=_task_reference_id(self),
            payload={
                'provider': provider,
                'dispatched': dispatched,
                'suppressed': suppressed,
                'sent': sent,
                'failed': failed,
            },
        )
        session.commit()
        return {'dispatched': dispatched, 'suppressed': suppressed, 'sent': sent, 'failed': failed}
    except Exception as exc:
        session.rollback()
        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type='notification_async_failed',
            reference_id=_task_reference_id(self),
            payload={
                'provider': provider,
                'min_risk_score': min_risk_score,
                'webhook_url': webhook_url,
                'dedup_window_minutes': dedup_window_minutes,
                'dedup_policy_by_risk': dedup_policy_by_risk,
                'error': str(exc),
                'error_type': type(exc).__name__,
            },
        )
        session.commit()
        raise
    finally:
        session.close()


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def ticket_sync_job(self, tenant_id: str, provider: str, case_ids: list[int]) -> dict:
    session = get_session()
    try:
        synced = sync_tickets(session, tenant_id, provider, case_ids)
        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type='ticket_sync_async_finished',
            reference_id=_task_reference_id(self),
            payload={
                'provider': provider,
                'synced': synced,
            },
        )
        session.commit()
        return {'synced': synced}
    except Exception as exc:
        session.rollback()
        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type='ticket_sync_async_failed',
            reference_id=_task_reference_id(self),
            payload={
                'provider': provider,
                'case_ids': case_ids,
                'error': str(exc),
                'error_type': type(exc).__name__,
            },
        )
        session.commit()
        raise
    finally:
        session.close()
