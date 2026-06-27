from pydantic import BaseModel, Field


class ScheduledReportConfig(BaseModel):
    name: str = Field(min_length=1, description='????')
    report_type: str = Field(pattern='^(vuln_summary|sla_overview|risk_trend)$', description='????')
    cron_expression: str = Field(default='0 9 * * 1', description='Cron ????????? 9:00?')
    provider: str = Field(min_length=1, description='????', examples=['webhook', 'feishu', 'dingtalk', 'wecom'])
    webhook_url: str = Field(min_length=1, description='????')
    enabled: bool = Field(default=True, description='????')
    description: str = Field(default='', description='??')


class ScheduledReportResponse(BaseModel):
    report_id: int
    tenant_id: str
    config: ScheduledReportConfig


class ScheduledReportListResponse(BaseModel):
    tenant_id: str
    total: int
    items: list[ScheduledReportResponse]
