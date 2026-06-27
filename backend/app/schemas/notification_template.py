from pydantic import BaseModel, Field


class NotificationTemplate(BaseModel):
    name: str = Field(min_length=1, description='????')
    provider: str = Field(min_length=1, description='?????', examples=['feishu', 'dingtalk', 'wecom', 'webhook'])
    title_template: str = Field(default='???? #{case_id}', description='????')
    body_template: str = Field(default='??: {tenant_id}\\n??: {state}\\n????: {risk_score}', description='????')
    enabled: bool = Field(default=True, description='????')


class NotificationTemplateResponse(BaseModel):
    template_id: int
    tenant_id: str
    config: NotificationTemplate


class NotificationTemplateListResponse(BaseModel):
    tenant_id: str
    total: int
    items: list[NotificationTemplateResponse]
