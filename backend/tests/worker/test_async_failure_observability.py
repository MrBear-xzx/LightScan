from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.event import Event
from app.workers import jobs


def test_dispatch_notification_job_logs_failure_event_on_exception(monkeypatch) -> None:
    def _raise_dispatch(*args, **kwargs):
        raise RuntimeError('dispatch boom')

    monkeypatch.setattr(jobs, 'dispatch_notifications', _raise_dispatch)

    try:
        jobs.dispatch_notification_job.delay(
            tenant_id='t1',
            min_risk_score=7.0,
            provider='webhook',
            webhook_url=None,
        )
    except Exception:
        pass

    engine = get_engine()
    with Session(engine) as session:
        event = session.execute(
            select(Event)
            .where(Event.event_type == 'notification_async_failed')
            .where(Event.tenant_id == 't1')
        ).scalar_one_or_none()

    assert event is not None


def test_ticket_sync_job_logs_failure_event_on_exception(monkeypatch) -> None:
    def _raise_sync(*args, **kwargs):
        raise RuntimeError('ticket sync boom')

    monkeypatch.setattr(jobs, 'sync_tickets', _raise_sync)

    try:
        jobs.ticket_sync_job.delay(
            tenant_id='t1',
            provider='mock_jira',
            case_ids=[1],
        )
    except Exception:
        pass

    engine = get_engine()
    with Session(engine) as session:
        event = session.execute(
            select(Event)
            .where(Event.event_type == 'ticket_sync_async_failed')
            .where(Event.tenant_id == 't1')
        ).scalar_one_or_none()

    assert event is not None
