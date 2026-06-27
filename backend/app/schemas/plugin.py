from pydantic import BaseModel, Field


class PluginRolloutRule(BaseModel):
    status: str = Field(pattern='^(enabled|disabled)$')
    rollout: str = Field(pattern='^(stable|canary)$')


class PluginRolloutPolicyUpsertRequest(BaseModel):
    tenant_id: str
    plugins: dict[str, PluginRolloutRule]


class PluginRolloutPolicyResponse(BaseModel):
    tenant_id: str
    plugins: dict[str, PluginRolloutRule]


class PluginRolloutPolicyDiffItem(BaseModel):
    before: PluginRolloutRule | None = None
    after: PluginRolloutRule | None = None


class PluginRolloutPolicyUpsertResponse(PluginRolloutPolicyResponse):
    diff: dict[str, PluginRolloutPolicyDiffItem]


class PluginRolloutAuditItem(BaseModel):
    event_id: int
    event_type: str
    created_at: str
    payload: dict


class PluginRolloutAuditResponse(BaseModel):
    tenant_id: str
    page: int
    page_size: int
    total: int
    items: list[PluginRolloutAuditItem]
