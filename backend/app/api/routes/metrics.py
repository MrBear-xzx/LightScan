import json

from fastapi import APIRouter, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.event import Event
from app.models.scan_task import ScanTask
from app.plugins.registry import build_default_registry

router = APIRouter(tags=['system'])


@router.get(
    '/metrics',
    summary='导出指标',
    description='导出 Prometheus 文本指标，包含任务与通知派发关键计数。',
    response_description='Prometheus 文本格式指标',
)
def metrics() -> Response:
    engine = get_engine()
    with Session(engine) as session:
        total_tasks = session.execute(select(func.count()).select_from(ScanTask)).scalar_one()
        discovery_tasks = session.execute(
            select(func.count())
            .select_from(ScanTask)
            .where(ScanTask.task_type == 'discover')
        ).scalar_one()
        notification_dispatched = session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.event_type == 'notification_dispatched')
        ).scalar_one()
        notification_async_queued = session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.event_type == 'notification_async_queued')
        ).scalar_one()
        ticket_sync_async_queued = session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.event_type == 'ticket_sync_async_queued')
        ).scalar_one()
        notification_async_failed = session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.event_type == 'notification_async_failed')
        ).scalar_one()
        ticket_sync_async_failed = session.execute(
            select(func.count())
            .select_from(Event)
            .where(Event.event_type == 'ticket_sync_async_failed')
        ).scalar_one()

        retry_rows = session.execute(
            select(Event.payload_json)
            .where(Event.event_type == 'job_retry_requested')
        ).all()
        job_retry_requested = len(retry_rows)

        retry_job_ids: set[str] = set()
        for row in retry_rows:
            payload = json.loads(row[0])
            retry_job_id = str(payload.get('new_job_id', ''))
            if retry_job_id:
                retry_job_ids.add(retry_job_id)

        if retry_job_ids:
            job_retry_failed = session.execute(
                select(func.count())
                .select_from(Event)
                .where(
                    Event.event_type.in_(
                        [
                            'notification_async_failed',
                            'ticket_sync_async_failed',
                        ]
                    )
                )
                .where(Event.reference_id.in_(list(retry_job_ids)))
            ).scalar_one()
        else:
            job_retry_failed = 0

    registry = build_default_registry()
    plugins = registry.list_plugins()
    plugins_total = len(plugins)
    plugins_healthy = 0
    for item in plugins:
        status = str(item.plugin.health().get('status', 'unknown'))
        if status == 'healthy':
            plugins_healthy += 1
    plugins_unhealthy = plugins_total - plugins_healthy

    retry_success_rate = 0.0
    if job_retry_requested > 0:
        retry_success_rate = round(
            max(0.0, (job_retry_requested - int(job_retry_failed)) / job_retry_requested),
            4,
        )

    body = '\n'.join(
        [
            '# HELP lightscan_tasks_total Total tasks observed',
            '# TYPE lightscan_tasks_total counter',
            f'lightscan_tasks_total {int(total_tasks)}',
            '# HELP lightscan_discovery_tasks_total Total discovery tasks observed',
            '# TYPE lightscan_discovery_tasks_total counter',
            f'lightscan_discovery_tasks_total {int(discovery_tasks)}',
            '# HELP lightscan_notification_dispatched_total Total dispatched notifications',
            '# TYPE lightscan_notification_dispatched_total counter',
            f'lightscan_notification_dispatched_total {int(notification_dispatched)}',
            '# HELP lightscan_notification_async_queued_total Total async notification jobs queued',
            '# TYPE lightscan_notification_async_queued_total counter',
            f'lightscan_notification_async_queued_total {int(notification_async_queued)}',
            '# HELP lightscan_ticket_sync_async_queued_total Total async ticket sync jobs queued',
            '# TYPE lightscan_ticket_sync_async_queued_total counter',
            f'lightscan_ticket_sync_async_queued_total {int(ticket_sync_async_queued)}',
            '# HELP lightscan_notification_async_failed_total Total async notification jobs failed',
            '# TYPE lightscan_notification_async_failed_total counter',
            f'lightscan_notification_async_failed_total {int(notification_async_failed)}',
            '# HELP lightscan_ticket_sync_async_failed_total Total async ticket sync jobs failed',
            '# TYPE lightscan_ticket_sync_async_failed_total counter',
            f'lightscan_ticket_sync_async_failed_total {int(ticket_sync_async_failed)}',
            '# HELP lightscan_job_retry_requested_total Total retry requests observed',
            '# TYPE lightscan_job_retry_requested_total counter',
            f'lightscan_job_retry_requested_total {int(job_retry_requested)}',
            '# HELP lightscan_job_retry_failed_total Total retry jobs failed',
            '# TYPE lightscan_job_retry_failed_total counter',
            f'lightscan_job_retry_failed_total {int(job_retry_failed)}',
            '# HELP lightscan_job_retry_success_rate Retry success rate in [0,1]',
            '# TYPE lightscan_job_retry_success_rate gauge',
            f'lightscan_job_retry_success_rate {retry_success_rate}',
            '# HELP lightscan_plugins_total Total plugins registered',
            '# TYPE lightscan_plugins_total gauge',
            f'lightscan_plugins_total {plugins_total}',
            '# HELP lightscan_plugins_healthy_total Total healthy plugins',
            '# TYPE lightscan_plugins_healthy_total gauge',
            f'lightscan_plugins_healthy_total {plugins_healthy}',
            '# HELP lightscan_plugins_unhealthy_total Total unhealthy plugins',
            '# TYPE lightscan_plugins_unhealthy_total gauge',
            f'lightscan_plugins_unhealthy_total {plugins_unhealthy}',
        ]
    )
    return Response(content=body, media_type='text/plain; version=0.0.4')
