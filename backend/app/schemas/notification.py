from pydantic import BaseModel, Field


class NotificationPreviewItem(BaseModel):
    case_id: int
    state: str
    risk_score: float
    owner: str | None


class NotificationPreviewResponse(BaseModel):
    tenant_id: str
    min_risk_score: float
    items: list[NotificationPreviewItem]


class NotificationDispatchRequest(BaseModel):
    tenant_id: str
    min_risk_score: float = 7.0
    provider: str = Field(default='webhook', pattern='^(webhook|feishu)$')
    webhook_url: str | None = None
    mode: str = Field(default='sync', pattern='^(sync|async)$')
    dedup_window_minutes: int | None = Field(default=None, ge=1, le=1440)
    dedup_policy_by_risk: dict[str, int] | None = None


class NotificationDispatchResponse(BaseModel):
    tenant_id: str
    provider: str
    mode: str
    job_id: str | None = None
    min_risk_score: float
    dedup_window_minutes: int
    dispatched: int
    suppressed: int
    sent: int
    failed: int


class NotificationPolicyUpsertRequest(BaseModel):
    tenant_id: str
    dedup_window_minutes: int = Field(default=30, ge=1, le=1440)
    dedup_policy_by_risk: dict[str, int] | None = None


class NotificationPolicyResponse(BaseModel):
    tenant_id: str
    dedup_window_minutes: int
    dedup_policy_by_risk: dict[str, int] | None = None
