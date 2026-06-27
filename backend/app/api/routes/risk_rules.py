from fastapi import APIRouter, Query

from app.schemas.risk_rules import RiskRuleConfig, RiskRuleResponse
from app.services.risk_rules_service import get_risk_rules, upsert_risk_rules

router = APIRouter(prefix='/api/v1/risk', tags=['risk'])


@router.get(
    '/rules',
    response_model=RiskRuleResponse,
    summary='获取风险评分规则配置',
    description='返回租户级风险评分规则（权重、严重等级映射、风险等级阈值），未配置时返回默认值。',
)
def get_rules(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> RiskRuleResponse:
    return get_risk_rules(tenant_id)


@router.put(
    '/rules',
    response_model=RiskRuleResponse,
    summary='设置风险评分规则配置',
)
def put_rules(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
    config: RiskRuleConfig = ...,
) -> RiskRuleResponse:
    return upsert_risk_rules(tenant_id, config)
