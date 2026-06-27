from fastapi import APIRouter, Query

from app.schemas.vuln_lifecycle import VulnerabilityLifecycleResponse
from app.services.vuln_lifecycle_service import query_vuln_lifecycle

router = APIRouter(prefix='/api/v1/reports/vuln', tags=['reports'])


@router.get(
    '/lifecycle',
    response_model=VulnerabilityLifecycleResponse,
    summary='漏洞生命周期仪表盘',
    description='返回漏洞状态分布、新增趋势、平均存在时间等生命周期指标。',
)
def lifecycle(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> VulnerabilityLifecycleResponse:
    return query_vuln_lifecycle(tenant_id)
