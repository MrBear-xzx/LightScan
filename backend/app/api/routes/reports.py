from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.tenant_guard import require_tenant_guard
from app.db.session import get_engine
from app.schemas.reporting import (
    OwnerSlaStats,
    SlaOverviewResponse,
    SlaOverviewStatusCounts,
    SlaTrendPoint,
    SlaTrendResponse,
    VulnSummaryCounts,
    VulnSummaryResponse,
)
from app.services.reporting_service import export_vuln_csv, get_sla_overview, get_sla_trend, get_vuln_summary

router = APIRouter(prefix='/api/v1/reports', tags=['reports'])


@router.get('/vuln/summary', response_model=VulnSummaryResponse, summary='漏洞报表汇总')
def vuln_summary(tenant_id: str = Depends(require_tenant_guard)) -> VulnSummaryResponse:
    engine = get_engine()
    with Session(engine) as session:
        counts = get_vuln_summary(session, tenant_id)
    return VulnSummaryResponse(tenant_id=tenant_id, counts=VulnSummaryCounts(**counts))


@router.get('/vuln/export.csv', summary='漏洞报表CSV导出')
def export_vuln_report_csv(tenant_id: str = Depends(require_tenant_guard)) -> Response:
    engine = get_engine()
    with Session(engine) as session:
        content = export_vuln_csv(session, tenant_id)

    return Response(
        content=content,
        media_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="vuln-report-{tenant_id}.csv"'},
    )


@router.get('/sla/overview', response_model=SlaOverviewResponse, summary='SLA看板总览')
def sla_overview(tenant_id: str = Depends(require_tenant_guard)) -> SlaOverviewResponse:
    engine = get_engine()
    with Session(engine) as session:
        data = get_sla_overview(session, tenant_id)

    return SlaOverviewResponse(
        tenant_id=data['tenant_id'],
        total_cases=data['total_cases'],
        overdue_cases=data['overdue_cases'],
        due_48h_cases=data['due_48h_cases'],
        no_sla_cases=data['no_sla_cases'],
        status_counts=SlaOverviewStatusCounts(**data['status_counts']),
        owner_breakdown={
            owner: OwnerSlaStats(**stats)
            for owner, stats in data['owner_breakdown'].items()
        },
    )


@router.get('/sla/trend', response_model=SlaTrendResponse, summary='SLA趋势')
def sla_trend(
    tenant_id: str = Depends(require_tenant_guard),
    days: int = Query(default=7, ge=1, le=30),
    granularity: str = Query(default='day', pattern='^(day|week)$'),
) -> SlaTrendResponse:
    engine = get_engine()
    with Session(engine) as session:
        points = get_sla_trend(session, tenant_id, days, granularity)

    return SlaTrendResponse(
        tenant_id=tenant_id,
        days=days,
        granularity=granularity,
        points=[SlaTrendPoint(**item) for item in points],
    )
