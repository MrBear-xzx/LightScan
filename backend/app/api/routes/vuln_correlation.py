from fastapi import APIRouter, Query

from app.schemas.vuln_correlation import VulnCorrelationResponse
from app.services.vuln_correlation_service import query_vuln_correlation

router = APIRouter(prefix='/api/v1/vuln-cases', tags=['vuln-cases'])


@router.get(
    '/correlation',
    response_model=VulnCorrelationResponse,
    summary='漏洞关联分析（按资产聚合）',
    description='按资产维度聚合漏洞案例，返回各资产的漏洞分布与最高风险漏洞摘要。',
)
def correlation(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> VulnCorrelationResponse:
    return query_vuln_correlation(tenant_id)
