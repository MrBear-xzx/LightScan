from pydantic import BaseModel, Field


class WebhookSubscription(BaseModel):
    url: str = Field(min_length=1, description='Webhook URL')
    event_types: list[str] = Field(min_length=1, description='?????????')
    enabled: bool = Field(default=True, description='????')
    description: str = Field(default='', description='????')


class WebhookSubscriptionResponse(BaseModel):
    sub_id: int
    tenant_id: str
    config: WebhookSubscription


class WebhookSubscriptionListResponse(BaseModel):
    tenant_id: str
    total: int
    items: list[WebhookSubscriptionResponse]
