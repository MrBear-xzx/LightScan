from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.alert_rule import AlertRuleConfig, AlertRuleListResponse, AlertRuleResponse
from app.services.alert_rule_service import (
    create_alert_rule,
    delete_alert_rule,
    get_alert_rule,
    list_alert_rules,
)

router = APIRouter(prefix='/api/v1/ops/alert-rules', tags=['ops'])


@router.get(
    '',
    response_model=AlertRuleListResponse,
    summary='告警规则列表',
)
def get_rules(
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> AlertRuleListResponse:
    return list_alert_rules(tenant_id)


@router.get(
    '/{rule_id}',
    response_model=AlertRuleResponse,
    summary='获取告警规则详情',
)
def get_rule(
    rule_id: int,
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> AlertRuleResponse:
    result = get_alert_rule(tenant_id, rule_id)
    if result is None:
        raise HTTPException(status_code=404, detail='rule not found')
    return result


@router.post(
    '',
    response_model=AlertRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary='创建告警规则',
)
def post_rule(
    payload: AlertRuleConfig,
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> AlertRuleResponse:
    return create_alert_rule(tenant_id, payload)


@router.delete(
    '/{rule_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='删除告警规则',
)
def remove_rule(
    rule_id: int,
    tenant_id: str = Query(default='default', min_length=1, description='租户标识'),
) -> None:
    deleted = delete_alert_rule(tenant_id, rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='rule not found')
