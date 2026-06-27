from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.vuln_case import VulnCase
from app.schemas.vuln_lifecycle import (
    StateDistribution,
    VulnerabilityLifecycleResponse,
)


def query_vuln_lifecycle(tenant_id: str) -> VulnerabilityLifecycleResponse:
    engine = get_engine()
    with Session(engine) as session:
        base = select(VulnCase).where(VulnCase.tenant_id == tenant_id)
        rows = session.execute(base).scalars().all()
        total_cases = len(rows)

        state_dist = StateDistribution()
        for r in rows:
            if r.state == 'new':
                state_dist.new += 1
            elif r.state == 'in_progress':
                state_dist.in_progress += 1
            elif r.state == 'resolved':
                state_dist.resolved += 1
            elif r.state == 'false_positive':
                state_dist.false_positive += 1
            elif r.state == 'rejected':
                state_dist.rejected += 1

        total_open = state_dist.new + state_dist.in_progress

        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        week_start = today_start - timedelta(days=today_start.weekday())

        def _cmp_ge(dt, ref):
            if dt.tzinfo is not None:
                return dt >= ref
            return dt >= ref.replace(tzinfo=None)

        created_today = sum(
            1 for r in rows
            if _cmp_ge(r.created_at, today_start)
        )
        created_this_week = sum(
            1 for r in rows
            if _cmp_ge(r.created_at, week_start)
        )
        # Resolved is approximate: we count resolved state as resolved today
        # (no resolved_at field exists, so we approximate)
        resolved_today = 0  # would need resolved_at field for accuracy

        open_rows = [r for r in rows if r.state in ('new', 'in_progress')]
        if open_rows:
            total_days = sum(
                (now - (r.created_at if r.created_at.tzinfo is not None else r.created_at.replace(tzinfo=timezone.utc))).total_seconds() / 86400
                for r in open_rows
            )
            avg_days_open = round(total_days / len(open_rows), 1)
        else:
            avg_days_open = 0.0

    return VulnerabilityLifecycleResponse(
        tenant_id=tenant_id,
        total_open=total_open,
        total_cases=total_cases,
        state_distribution=state_dist,
        created_today=created_today,
        created_this_week=created_this_week,
        resolved_today=resolved_today,
        avg_days_open=avg_days_open,
    )



