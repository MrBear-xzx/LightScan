from pydantic import BaseModel, Field


class SeverityWeightMap(BaseModel):
    critical: float = Field(default=9.0, ge=0, le=10)
    high: float = Field(default=7.0, ge=0, le=10)
    medium: float = Field(default=4.0, ge=0, le=10)
    low: float = Field(default=1.0, ge=0, le=10)
    unknown: float = Field(default=0.5, ge=0, le=10)


class RiskScoreWeights(BaseModel):
    severity_weight: float = Field(default=0.3, ge=0, le=1, description='??????')
    asset_criticality_weight: float = Field(default=0.25, ge=0, le=1, description='???????')
    exposure_weight: float = Field(default=0.2, ge=0, le=1, description='?????')
    exploitability_weight: float = Field(default=0.2, ge=0, le=1, description='??????')
    compensating_control_penalty: float = Field(default=0.05, ge=0, le=1, description='????????')


class RiskLevelThreshold(BaseModel):
    critical: float = Field(default=8.0, ge=0, le=10, description='?????>=?')
    high: float = Field(default=6.0, ge=0, le=10, description='?????>=?')
    medium: float = Field(default=3.0, ge=0, le=10, description='?????>=?')
    low: float = Field(default=0.0, ge=0, le=10, description='?????>=?')


class RiskRuleConfig(BaseModel):
    severity_map: SeverityWeightMap = Field(default_factory=SeverityWeightMap, description='????????')
    weights: RiskScoreWeights = Field(default_factory=RiskScoreWeights, description='????')
    thresholds: RiskLevelThreshold = Field(default_factory=RiskLevelThreshold, description='??????')


class RiskRuleResponse(BaseModel):
    tenant_id: str
    config: RiskRuleConfig


DEFAULT_RISK_RULES: RiskRuleConfig = RiskRuleConfig()
