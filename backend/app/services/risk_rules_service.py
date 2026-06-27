import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.policy import Policy
from app.schemas.risk_rules import (
    DEFAULT_RISK_RULES,
    RiskLevelThreshold,
    RiskRuleConfig,
    RiskRuleResponse,
)

_RISK_RULES_POLICY_NAME = 'risk_rules'


def _default_response(tenant_id: str) -> RiskRuleResponse:
    return RiskRuleResponse(tenant_id=tenant_id, config=DEFAULT_RISK_RULES)


def get_risk_rules(tenant_id: str) -> RiskRuleResponse:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.name == _RISK_RULES_POLICY_NAME)
            .order_by(Policy.policy_id.desc())
            .limit(1)
        ).scalar_one_or_none()
        if row is None:
            return _default_response(tenant_id)
        config_dict = json.loads(row.config_json)
        return RiskRuleResponse(
            tenant_id=tenant_id,
            config=RiskRuleConfig(**config_dict),
        )


def upsert_risk_rules(tenant_id: str, config: RiskRuleConfig) -> RiskRuleResponse:
    engine = get_engine()
    with Session(engine) as session:
        existing = session.execute(
            select(Policy)
            .where(Policy.tenant_id == tenant_id)
            .where(Policy.name == _RISK_RULES_POLICY_NAME)
            .order_by(Policy.policy_id.desc())
            .limit(1)
        ).scalar_one_or_none()
        config_json = json.dumps(config.model_dump(), ensure_ascii=False)
        if existing is None:
            row = Policy(
                tenant_id=tenant_id,
                name=_RISK_RULES_POLICY_NAME,
                config_json=config_json,
            )
            session.add(row)
        else:
            existing.config_json = config_json
        session.commit()
    return RiskRuleResponse(tenant_id=tenant_id, config=config)


def calculate_risk_score_with_rules(
    severity_str: str,
    asset_criticality: float = 5.0,
    exposure: float = 5.0,
    exploitability: float = 5.0,
    compensating_control: float = 0.0,
    rules: RiskRuleConfig | None = None,
) -> float:
    if rules is None:
        rules = DEFAULT_RISK_RULES

    sev = rules.severity_map.model_dump().get(severity_str.lower(), rules.severity_map.unknown)
    w = rules.weights
    score = (
        w.severity_weight * sev
        + w.asset_criticality_weight * asset_criticality
        + w.exposure_weight * exposure
        + w.exploitability_weight * exploitability
        - w.compensating_control_penalty * compensating_control
    )
    return max(0.0, min(10.0, round(score, 2)))


def classify_risk_level(score: float, thresholds: RiskLevelThreshold | None = None) -> str:
    if thresholds is None:
        thresholds = DEFAULT_RISK_RULES.thresholds
    if score >= thresholds.critical:
        return 'critical'
    if score >= thresholds.high:
        return 'high'
    if score >= thresholds.medium:
        return 'medium'
    return 'low'

