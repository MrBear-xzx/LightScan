from pydantic import BaseModel, Field


class AlertRuleMetric(BaseModel):
    metric_name: str = Field(description='????', examples=['lightscan_tasks_total'])
    operator: str = Field(pattern='^(>|<|>=|<=|==)$', description='?????')
    threshold: float = Field(description='??')
    duration_seconds: int = Field(default=300, ge=0, description='????')


class AlertRuleConfig(BaseModel):
    name: str = Field(min_length=1, description='????')
    enabled: bool = Field(default=True, description='????')
    severity: str = Field(default='warning', pattern='^(info|warning|critical)$', description='????')
    metrics: list[AlertRuleMetric] = Field(min_length=1, description='???????AND?')
    description: str = Field(default='', description='????')


class AlertRuleResponse(BaseModel):
    rule_id: int
    tenant_id: str
    config: AlertRuleConfig


class AlertRuleListResponse(BaseModel):
    tenant_id: str
    total: int
    items: list[AlertRuleResponse]
