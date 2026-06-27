import csv
import io
from datetime import datetime, timedelta, timezone

from sqlalchemy import Integer, func, select
from sqlalchemy.orm import Session

from app.models.vuln_case import VulnCase


def _default_status_counts() -> dict[str, int]:
    return {
        'new': 0,
        'confirmed': 0,
        'in_progress': 0,
        'fixed': 0,
        'ignored': 0,
        'reopened': 0,
    }


def get_vuln_summary(session: Session, tenant_id: str) -> dict[str, int]:
    rows = session.execute(
        select(VulnCase.state, func.count())
        .where(VulnCase.tenant_id == tenant_id)
        .group_by(VulnCase.state)
    ).all()
    result = _default_status_counts()
    for state, count in rows:
        if state in result:
            result[state] = int(count)
    return result


def export_vuln_csv(session: Session, tenant_id: str) -> str:
    rows = session.execute(
        select(
            VulnCase.case_id,
            VulnCase.tenant_id,
            VulnCase.state,
            VulnCase.risk_score,
            VulnCase.owner,
        )
        .where(VulnCase.tenant_id == tenant_id)
        .order_by(VulnCase.risk_score.desc(), VulnCase.case_id.asc())
    ).all()

    out = io.StringIO()
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(['case_id', 'tenant_id', 'state', 'risk_score', 'owner'])
    for row in rows:
        writer.writerow([row.case_id, row.tenant_id, row.state, row.risk_score, row.owner or ''])
    return out.getvalue()


def get_sla_overview(session: Session, tenant_id: str) -> dict:
    now = datetime.now(timezone.utc)
    next_48h = now + timedelta(hours=48)

    status_counts = get_vuln_summary(session, tenant_id)

    total_cases = session.execute(
        select(func.count())
        .select_from(VulnCase)
        .where(VulnCase.tenant_id == tenant_id)
    ).scalar_one()

    no_sla_cases = session.execute(
        select(func.count())
        .select_from(VulnCase)
        .where(VulnCase.tenant_id == tenant_id)
        .where(VulnCase.sla_due_at.is_(None))
    ).scalar_one()

    active_states = ['new', 'confirmed', 'in_progress', 'reopened']

    overdue_cases = session.execute(
        select(func.count())
        .select_from(VulnCase)
        .where(VulnCase.tenant_id == tenant_id)
        .where(VulnCase.state.in_(active_states))
        .where(VulnCase.sla_due_at.is_not(None))
        .where(VulnCase.sla_due_at < now)
    ).scalar_one()

    due_48h_cases = session.execute(
        select(func.count())
        .select_from(VulnCase)
        .where(VulnCase.tenant_id == tenant_id)
        .where(VulnCase.state.in_(active_states))
        .where(VulnCase.sla_due_at.is_not(None))
        .where(VulnCase.sla_due_at >= now)
        .where(VulnCase.sla_due_at <= next_48h)
    ).scalar_one()

    owner_rows = session.execute(
        select(
            VulnCase.owner,
            func.count().label('total_count'),
            func.sum(
                (VulnCase.state.in_(active_states) & VulnCase.sla_due_at.is_not(None) & (VulnCase.sla_due_at < now)).cast(Integer)
            ).label('overdue_count'),
        )
        .where(VulnCase.tenant_id == tenant_id)
        .group_by(VulnCase.owner)
    ).all()

    owner_breakdown: dict[str, dict[str, int]] = {}
    for owner, total_count, overdue_count in owner_rows:
        key = owner if owner else 'unassigned'
        owner_breakdown[key] = {
            'total_cases': int(total_count or 0),
            'overdue_cases': int(overdue_count or 0),
        }

    return {
        'tenant_id': tenant_id,
        'total_cases': int(total_cases),
        'overdue_cases': int(overdue_cases),
        'due_48h_cases': int(due_48h_cases),
        'no_sla_cases': int(no_sla_cases),
        'status_counts': status_counts,
        'owner_breakdown': owner_breakdown,
    }


def get_sla_trend(session: Session, tenant_id: str, days: int, granularity: str = 'day') -> list[dict]:
    now = datetime.now(timezone.utc)
    start_day = (now - timedelta(days=days - 1)).date()
    end_day = now.date()

    rows = session.execute(
        select(
            VulnCase.created_at,
            VulnCase.sla_due_at,
            VulnCase.state,
        )
        .where(VulnCase.tenant_id == tenant_id)
    ).all()

    active_states = {'new', 'confirmed', 'in_progress', 'reopened'}

    if granularity == 'week':
        bucket_count = max(1, (days + 6) // 7)
        points = [
            {'date': f'W{i + 1}', 'overdue_cases': 0, 'total_cases': 0}
            for i in range(bucket_count)
        ]
        for row in rows:
            created_date = row.created_at.date()
            if created_date < start_day or created_date > end_day:
                continue
            day_offset = (created_date - start_day).days
            bucket_idx = min(day_offset // 7, bucket_count - 1)
            points[bucket_idx]['total_cases'] += 1
            if row.state in active_states and row.sla_due_at is not None and row.sla_due_at < now:
                points[bucket_idx]['overdue_cases'] += 1
        return points

    points_map: dict[str, dict] = {}
    current = start_day
    while current <= end_day:
        key = current.isoformat()
        points_map[key] = {'date': key, 'overdue_cases': 0, 'total_cases': 0}
        current += timedelta(days=1)

    for row in rows:
        created_date = row.created_at.date()
        key = created_date.isoformat()
        if key not in points_map:
            continue

        points_map[key]['total_cases'] += 1
        if row.state in active_states and row.sla_due_at is not None and row.sla_due_at < now:
            points_map[key]['overdue_cases'] += 1

    return [points_map[key] for key in sorted(points_map.keys())]
