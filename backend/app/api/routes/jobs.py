import json
import csv
import io
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.tenant_guard import require_tenant_guard, validate_tenant_guard
from app.db.session import get_engine
from app.models.event import Event
from app.schemas.job import (
    JobRetryHistoryOverviewResponse,
    JobRetryPolicyResponse,
    JobRetryPolicyUpsertRequest,
    JobRetryHistoryResponse,
    JobRetryRequest,
    JobRetryResponse,
    JobStatusResponse,
)
from app.services.event_service import log_event_with_session
from app.services.job_policy_service import get_job_retry_policy, upsert_job_retry_policy
from app.workers.jobs import dispatch_notification_job, ticket_sync_job

router = APIRouter(prefix='/api/v1/jobs', tags=['jobs'])

QUEUED_EVENT_TYPES = {
    'notification_async_queued': 'notification',
    'ticket_sync_async_queued': 'ticket_sync',
}
SUCCESS_EVENT_TYPES = {
    'notification_async_finished': 'notification',
    'ticket_sync_async_finished': 'ticket_sync',
}
FAILED_EVENT_TYPES = {
    'notification_async_failed': 'notification',
    'ticket_sync_async_failed': 'ticket_sync',
}
MAX_RETRY_COUNT = 3
RETRY_COOLDOWN_SECONDS = 60


@router.get('/status', response_model=JobStatusResponse, summary='查询异步任务状态')
def job_status(
    tenant_id: str = Depends(require_tenant_guard),
    job_id: str = Query(min_length=1),
) -> JobStatusResponse:
    engine = get_engine()
    with Session(engine) as session:
        event = session.execute(
            select(Event)
            .where(Event.tenant_id == tenant_id)
            .where(Event.reference_id == job_id)
            .where(Event.event_type.in_(list(QUEUED_EVENT_TYPES | SUCCESS_EVENT_TYPES | FAILED_EVENT_TYPES)))
            .order_by(Event.event_id.desc())
            .limit(1)
        ).scalar_one_or_none()

    if event is None:
        raise HTTPException(status_code=404, detail='job not found')

    if event.event_type in SUCCESS_EVENT_TYPES:
        status = 'success'
        job_type = SUCCESS_EVENT_TYPES[event.event_type]
    elif event.event_type in FAILED_EVENT_TYPES:
        status = 'failed'
        job_type = FAILED_EVENT_TYPES[event.event_type]
    else:
        status = 'queued'
        job_type = QUEUED_EVENT_TYPES[event.event_type]

    payload = json.loads(event.payload_json)
    last_error = None
    retry_count = None
    last_retry_at = None
    if status == 'failed':
        last_error = payload.get('error')
        retry_count = int(payload.get('retry_count', 0))
        last_retry_at = payload.get('last_retry_at')

    return JobStatusResponse(
        tenant_id=tenant_id,
        job_id=job_id,
        job_type=job_type,
        status=status,
        updated_at=event.created_at,
        last_error=last_error,
        retry_count=retry_count,
        last_retry_at=last_retry_at,
    )


@router.post('/retry', response_model=JobRetryResponse, summary='重试失败异步任务')
def job_retry(
    payload: JobRetryRequest,
    x_tenant_id: str | None = Header(default=None, alias='X-Tenant-ID'),
) -> JobRetryResponse:
    tenant_id = validate_tenant_guard(payload.tenant_id, x_tenant_id)
    engine = get_engine()
    with Session(engine) as session:
        retry_policy = get_job_retry_policy(session, tenant_id)
        max_retry_count = int(retry_policy.get('max_retry_count', MAX_RETRY_COUNT))
        retry_cooldown_seconds = int(retry_policy.get('retry_cooldown_seconds', RETRY_COOLDOWN_SECONDS))
        failed_event = session.execute(
            select(Event)
            .where(Event.tenant_id == tenant_id)
            .where(Event.reference_id == payload.job_id)
            .where(Event.event_type.in_(list(FAILED_EVENT_TYPES)))
            .order_by(Event.event_id.desc())
            .limit(1)
        ).scalar_one_or_none()
        if failed_event is None:
            raise HTTPException(status_code=404, detail='failed job not found')

        failed_payload = json.loads(failed_event.payload_json)
        retry_count = int(failed_payload.get('retry_count', 0))
        if retry_count >= max_retry_count:
            raise HTTPException(status_code=409, detail='max retry count reached')
        last_retry_at = failed_payload.get('last_retry_at')
        if last_retry_at and retry_cooldown_seconds > 0:
            try:
                last_retry_dt = datetime.fromisoformat(last_retry_at.replace('Z', '+00:00'))
                if datetime.now(timezone.utc) - last_retry_dt < timedelta(seconds=retry_cooldown_seconds):
                    raise HTTPException(status_code=409, detail='retry cooldown not elapsed')
            except ValueError:
                pass
        retry_meta = {
            'retry_count': retry_count + 1,
            'last_retry_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        }
        retry_payload = {**failed_payload, **retry_meta}

        if failed_event.event_type == 'notification_async_failed':
            task = dispatch_notification_job.delay(
                tenant_id,
                float(retry_payload.get('min_risk_score', 7.0)),
                str(retry_payload.get('provider', 'webhook')),
                retry_payload.get('webhook_url'),
                int(retry_payload.get('dedup_window_minutes', 30)),
                retry_payload.get('dedup_policy_by_risk'),
            )
            job_type = 'notification'
            queued_event_type = 'notification_async_queued'
        else:
            task = ticket_sync_job.delay(
                tenant_id,
                str(retry_payload.get('provider', 'mock_jira')),
                list(retry_payload.get('case_ids', [])),
            )
            job_type = 'ticket_sync'
            queued_event_type = 'ticket_sync_async_queued'

        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type='job_retry_requested',
            reference_id=payload.job_id,
            payload={'new_job_id': task.id, 'job_type': job_type, **retry_meta},
        )
        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type=queued_event_type,
            reference_id=task.id,
            payload=retry_payload,
        )
        session.commit()

    return JobRetryResponse(
        tenant_id=tenant_id,
        source_job_id=payload.job_id,
        new_job_id=task.id,
        job_type=job_type,
        status='queued',
    )


@router.get('/retry-policy', response_model=JobRetryPolicyResponse, summary='查询任务重试策略')
def get_retry_policy(
    tenant_id: str = Depends(require_tenant_guard),
) -> JobRetryPolicyResponse:
    engine = get_engine()
    with Session(engine) as session:
        config = get_job_retry_policy(session, tenant_id)
    return JobRetryPolicyResponse(
        tenant_id=tenant_id,
        max_retry_count=int(config.get('max_retry_count', MAX_RETRY_COUNT)),
        retry_cooldown_seconds=int(config.get('retry_cooldown_seconds', RETRY_COOLDOWN_SECONDS)),
    )


@router.put('/retry-policy', response_model=JobRetryPolicyResponse, summary='设置任务重试策略')
def put_retry_policy(
    payload: JobRetryPolicyUpsertRequest,
    x_tenant_id: str | None = Header(default=None, alias='X-Tenant-ID'),
) -> JobRetryPolicyResponse:
    tenant_id = validate_tenant_guard(payload.tenant_id, x_tenant_id)
    engine = get_engine()
    with Session(engine) as session:
        config = upsert_job_retry_policy(
            session,
            tenant_id=tenant_id,
            max_retry_count=payload.max_retry_count,
            retry_cooldown_seconds=payload.retry_cooldown_seconds,
        )
        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type='job_retry_policy_updated',
            reference_id=tenant_id,
            payload=config,
        )
        session.commit()
    return JobRetryPolicyResponse(
        tenant_id=tenant_id,
        max_retry_count=int(config.get('max_retry_count', MAX_RETRY_COUNT)),
        retry_cooldown_seconds=int(config.get('retry_cooldown_seconds', RETRY_COOLDOWN_SECONDS)),
    )


def _build_retry_requested_event_query(
    tenant_id: str,
    job_type: str | None = None,
    job_id_keyword: str | None = None,
    new_job_id_keyword: str | None = None,
    requested_from: datetime | None = None,
    requested_to: datetime | None = None,
):
    query = (
        select(Event)
        .where(Event.tenant_id == tenant_id)
        .where(Event.event_type == 'job_retry_requested')
    )
    if requested_from:
        query = query.where(Event.created_at >= requested_from)
    if requested_to:
        query = query.where(Event.created_at <= requested_to)
    if job_type:
        query = query.where(
            or_(
                Event.payload_json.like(f'%"job_type": "{job_type}"%'),
                Event.payload_json.like(f'%"job_type":"{job_type}"%'),
            )
        )
    if job_id_keyword:
        query = query.where(Event.reference_id.contains(job_id_keyword))
    if new_job_id_keyword:
        query = query.where(
            or_(
                Event.payload_json.like(f'%"new_job_id": "%{new_job_id_keyword}%"%'),
                Event.payload_json.like(f'%"new_job_id":"%{new_job_id_keyword}%"%'),
            )
        )
    return query


@router.get('/retries', response_model=JobRetryHistoryResponse, summary='查询任务重试历史')
def job_retry_history(
    tenant_id: str = Depends(require_tenant_guard),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    columns: str | None = Query(default=None),
    sort_order: str = Query(default='desc', pattern='^(asc|desc)$'),
    job_type: str | None = Query(default=None, pattern='^(notification|ticket_sync)$'),
    job_id_keyword: str | None = Query(default=None, min_length=1),
    new_job_id_keyword: str | None = Query(default=None, min_length=1),
    requested_from: datetime | None = Query(default=None),
    requested_to: datetime | None = Query(default=None),
) -> JobRetryHistoryResponse:
    if requested_from and requested_to and requested_from > requested_to:
        raise HTTPException(status_code=400, detail='requested_from must be earlier than requested_to')

    allowed_columns = ['job_id', 'new_job_id', 'job_type', 'retry_count', 'requested_at']
    selected_columns = allowed_columns
    if columns:
        selected_columns = [item.strip() for item in columns.split(',') if item.strip()]
        if not selected_columns or any(item not in allowed_columns for item in selected_columns):
            raise HTTPException(status_code=400, detail='invalid columns parameter')

    engine = get_engine()
    offset = (page - 1) * page_size
    with Session(engine) as session:
        query = _build_retry_requested_event_query(
            tenant_id=tenant_id,
            job_type=job_type,
            job_id_keyword=job_id_keyword,
            new_job_id_keyword=new_job_id_keyword,
            requested_from=requested_from,
            requested_to=requested_to,
        )
        total = session.execute(select(func.count()).select_from(query.subquery())).scalar_one()
        if sort_order == 'asc':
            rows = session.execute(
                query.order_by(Event.event_id.asc()).offset(offset).limit(page_size)
            ).scalars().all()
        else:
            rows = session.execute(
                query.order_by(Event.event_id.desc()).offset(offset).limit(page_size)
            ).scalars().all()

    items: list[dict] = []
    for row in rows:
        payload = json.loads(row.payload_json)
        value_map = {
            'job_id': row.reference_id,
            'new_job_id': str(payload.get('new_job_id', '')),
            'job_type': str(payload.get('job_type', 'unknown')),
            'retry_count': int(payload.get('retry_count', 0)),
            'requested_at': row.created_at.isoformat(),
        }
        items.append({column: value_map[column] for column in selected_columns})

    return JobRetryHistoryResponse(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        total=total,
        items=items,
    )


@router.get('/retries/export.csv', summary='导出任务重试历史CSV')
def export_job_retry_history_csv(
    tenant_id: str = Depends(require_tenant_guard),
    sort_order: str = Query(default='desc', pattern='^(asc|desc)$'),
    job_type: str | None = Query(default=None, pattern='^(notification|ticket_sync)$'),
    job_id_keyword: str | None = Query(default=None, min_length=1),
    new_job_id_keyword: str | None = Query(default=None, min_length=1),
    columns: str | None = Query(default=None),
    requested_from: datetime | None = Query(default=None),
    requested_to: datetime | None = Query(default=None),
) -> Response:
    if requested_from and requested_to and requested_from > requested_to:
        raise HTTPException(status_code=400, detail='requested_from must be earlier than requested_to')

    allowed_columns = ['job_id', 'new_job_id', 'job_type', 'retry_count', 'requested_at']
    selected_columns = allowed_columns
    if columns:
        selected_columns = [item.strip() for item in columns.split(',') if item.strip()]
        if not selected_columns or any(item not in allowed_columns for item in selected_columns):
            raise HTTPException(status_code=400, detail='invalid columns parameter')

    engine = get_engine()
    with Session(engine) as session:
        query = _build_retry_requested_event_query(
            tenant_id=tenant_id,
            job_type=job_type,
            job_id_keyword=job_id_keyword,
            new_job_id_keyword=new_job_id_keyword,
            requested_from=requested_from,
            requested_to=requested_to,
        )
        if sort_order == 'asc':
            rows = session.execute(query.order_by(Event.event_id.asc())).scalars().all()
        else:
            rows = session.execute(query.order_by(Event.event_id.desc())).scalars().all()

    out = io.StringIO()
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(selected_columns)

    for row in rows:
        payload = json.loads(row.payload_json)
        current_new_job_id = str(payload.get('new_job_id', ''))
        value_map = {
            'job_id': row.reference_id,
            'new_job_id': current_new_job_id,
            'job_type': str(payload.get('job_type', 'unknown')),
            'retry_count': int(payload.get('retry_count', 0)),
            'requested_at': row.created_at.isoformat(),
        }
        writer.writerow([value_map[column] for column in selected_columns])

    return Response(
        content=out.getvalue(),
        media_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="job-retry-history-{tenant_id}.csv"'},
    )


@router.get('/retries/overview', response_model=JobRetryHistoryOverviewResponse, summary='任务重试历史总览')
def job_retry_history_overview(
    tenant_id: str = Depends(require_tenant_guard),
    job_type: str | None = Query(default=None, pattern='^(notification|ticket_sync)$'),
    job_id_keyword: str | None = Query(default=None, min_length=1),
    new_job_id_keyword: str | None = Query(default=None, min_length=1),
    requested_from: datetime | None = Query(default=None),
    requested_to: datetime | None = Query(default=None),
) -> JobRetryHistoryOverviewResponse:
    if requested_from and requested_to and requested_from > requested_to:
        raise HTTPException(status_code=400, detail='requested_from must be earlier than requested_to')

    engine = get_engine()
    with Session(engine) as session:
        query = _build_retry_requested_event_query(
            tenant_id=tenant_id,
            job_type=job_type,
            job_id_keyword=job_id_keyword,
            new_job_id_keyword=new_job_id_keyword,
            requested_from=requested_from,
            requested_to=requested_to,
        )
        rows = session.execute(query).scalars().all()

    job_type_counts: dict[str, int] = {'notification': 0, 'ticket_sync': 0, 'unknown': 0}
    retry_count_distribution: dict[str, int] = {}
    retry_counts: list[int] = []
    source_job_ids: set[str] = set()
    first_retry_requested_at: str | None = None
    last_retry_requested_at: str | None = None
    first_sort_key: tuple[datetime, int] | None = None
    last_sort_key: tuple[datetime, int] | None = None
    latest_retry_count = 0
    latest_retry_job_type: str | None = None
    latest_source_job_id: str | None = None
    for row in rows:
        payload = json.loads(row.payload_json)
        current_job_type = str(payload.get('job_type', 'unknown'))
        retry_count = int(payload.get('retry_count', 0))
        if current_job_type not in job_type_counts:
            job_type_counts[current_job_type] = 0
        job_type_counts[current_job_type] += 1
        retry_counts.append(retry_count)
        retry_count_key = str(retry_count)
        retry_count_distribution[retry_count_key] = retry_count_distribution.get(retry_count_key, 0) + 1
        source_job_ids.add(row.reference_id)
        current_sort_key = (row.created_at, row.event_id)
        if first_sort_key is None or current_sort_key < first_sort_key:
            first_sort_key = current_sort_key
            first_retry_requested_at = row.created_at.isoformat()
        if last_sort_key is None or current_sort_key > last_sort_key:
            last_sort_key = current_sort_key
            last_retry_requested_at = row.created_at.isoformat()
            latest_retry_count = retry_count
            latest_retry_job_type = current_job_type
            latest_source_job_id = row.reference_id

    max_retry_count = max(retry_counts) if retry_counts else 0
    avg_retry_count = round(sum(retry_counts) / len(retry_counts), 2) if retry_counts else 0.0

    return JobRetryHistoryOverviewResponse(
        tenant_id=tenant_id,
        total_retries=len(retry_counts),
        unique_source_jobs=len(source_job_ids),
        job_type_counts=job_type_counts,
        retry_count_distribution=retry_count_distribution,
        max_retry_count=max_retry_count,
        avg_retry_count=avg_retry_count,
        latest_retry_count=latest_retry_count,
        latest_retry_job_type=latest_retry_job_type,
        latest_source_job_id=latest_source_job_id,
        first_retry_requested_at=first_retry_requested_at,
        last_retry_requested_at=last_retry_requested_at,
    )
