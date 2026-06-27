from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.scheduled_report import (
    ScheduledReportConfig,
    ScheduledReportListResponse,
    ScheduledReportResponse,
)
from app.services.scheduled_report_service import (
    create_report,
    delete_report,
    list_reports,
)

router = APIRouter(prefix='/api/v1/reports/scheduled', tags=['reports'])


@router.get('', response_model=ScheduledReportListResponse)
def get_reports(tenant_id: str = Query(default='default')) -> ScheduledReportListResponse:
    return list_reports(tenant_id)


@router.post('', response_model=ScheduledReportResponse, status_code=status.HTTP_201_CREATED)
def post_report(payload: ScheduledReportConfig, tenant_id: str = Query(default='default')) -> ScheduledReportResponse:
    return create_report(tenant_id, payload)


@router.delete('/{report_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_report(report_id: int, tenant_id: str = Query(default='default')) -> None:
    deleted = delete_report(tenant_id, report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='report not found')
