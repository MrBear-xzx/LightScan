from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.api.tenant_guard import require_tenant_guard, validate_tenant_guard
from app.db.session import get_engine
from app.schemas.notification import (
    NotificationDispatchRequest,
    NotificationDispatchResponse,
    NotificationPolicyResponse,
    NotificationPolicyUpsertRequest,
    NotificationPreviewItem,
    NotificationPreviewResponse,
)
from app.services.notification_service import (
    dispatch_notifications,
    get_notification_policy,
    preview_notifications,
    upsert_notification_policy,
)
from app.services.event_service import log_event_with_session
from app.workers.jobs import dispatch_notification_job

router = APIRouter(prefix='/api/v1/notifications', tags=['notifications'])


@router.get('/preview', response_model=NotificationPreviewResponse, summary='通知预览')
def notify_preview(
    tenant_id: str = Depends(require_tenant_guard),
    min_risk_score: float = Query(default=7.0, ge=0.0, le=10.0),
) -> NotificationPreviewResponse:
    engine = get_engine()
    with Session(engine) as session:
        rows = preview_notifications(session, tenant_id, min_risk_score)

    items = [
        NotificationPreviewItem(
            case_id=row.case_id,
            state=row.state,
            risk_score=row.risk_score,
            owner=row.owner,
        )
        for row in rows
    ]
    return NotificationPreviewResponse(tenant_id=tenant_id, min_risk_score=min_risk_score, items=items)


@router.post('/dispatch', response_model=NotificationDispatchResponse, summary='通知派发（模拟）')
def notify_dispatch(
    payload: NotificationDispatchRequest,
    x_tenant_id: str | None = Header(default=None, alias='X-Tenant-ID'),
) -> NotificationDispatchResponse:
    tenant_id = validate_tenant_guard(payload.tenant_id, x_tenant_id)
    engine = get_engine()
    with Session(engine) as session:
        policy = get_notification_policy(session, tenant_id) or {}
    dedup_window_minutes = payload.dedup_window_minutes or int(policy.get('dedup_window_minutes', 30))
    dedup_policy_by_risk = payload.dedup_policy_by_risk
    if dedup_policy_by_risk is None:
        dedup_policy_by_risk = policy.get('dedup_policy_by_risk')

    if payload.mode == 'async':
        task = dispatch_notification_job.delay(
            tenant_id,
            payload.min_risk_score,
            payload.provider,
            payload.webhook_url,
            dedup_window_minutes,
            dedup_policy_by_risk,
        )
        with Session(engine) as session:
            log_event_with_session(
                session,
                tenant_id=tenant_id,
                event_type='notification_async_queued',
                reference_id=task.id,
                payload={
                    'provider': payload.provider,
                    'min_risk_score': payload.min_risk_score,
                    'dedup_window_minutes': dedup_window_minutes,
                    'dedup_policy_by_risk': dedup_policy_by_risk,
                },
            )
            session.commit()
        return NotificationDispatchResponse(
            tenant_id=tenant_id,
            provider=payload.provider,
            mode='async',
            job_id=task.id,
            min_risk_score=payload.min_risk_score,
            dedup_window_minutes=dedup_window_minutes,
            dispatched=0,
            suppressed=0,
            sent=0,
            failed=0,
        )

    with Session(engine) as session:
        dispatched, suppressed, sent, failed = dispatch_notifications(
            session,
            tenant_id,
            payload.min_risk_score,
            payload.provider,
            payload.webhook_url,
            dedup_window_minutes,
            dedup_policy_by_risk,
        )

    return NotificationDispatchResponse(
        tenant_id=tenant_id,
        provider=payload.provider,
        mode='sync',
        min_risk_score=payload.min_risk_score,
        dedup_window_minutes=dedup_window_minutes,
        dispatched=dispatched,
        suppressed=suppressed,
        sent=sent,
        failed=failed,
    )


@router.get('/policy', response_model=NotificationPolicyResponse, summary='查询通知策略')
def get_policy(
    tenant_id: str = Depends(require_tenant_guard),
) -> NotificationPolicyResponse:
    engine = get_engine()
    with Session(engine) as session:
        policy = get_notification_policy(session, tenant_id) or {}
    return NotificationPolicyResponse(
        tenant_id=tenant_id,
        dedup_window_minutes=int(policy.get('dedup_window_minutes', 30)),
        dedup_policy_by_risk=policy.get('dedup_policy_by_risk'),
    )


@router.put('/policy', response_model=NotificationPolicyResponse, summary='设置通知策略')
def put_policy(
    payload: NotificationPolicyUpsertRequest,
    x_tenant_id: str | None = Header(default=None, alias='X-Tenant-ID'),
) -> NotificationPolicyResponse:
    tenant_id = validate_tenant_guard(payload.tenant_id, x_tenant_id)
    engine = get_engine()
    with Session(engine) as session:
        config = upsert_notification_policy(
            session,
            tenant_id=tenant_id,
            dedup_window_minutes=payload.dedup_window_minutes,
            dedup_policy_by_risk=payload.dedup_policy_by_risk,
        )
    return NotificationPolicyResponse(
        tenant_id=tenant_id,
        dedup_window_minutes=int(config.get('dedup_window_minutes', 30)),
        dedup_policy_by_risk=config.get('dedup_policy_by_risk'),
    )
