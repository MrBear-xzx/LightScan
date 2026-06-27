from datetime import datetime

from pydantic import BaseModel, Field


class VulnCaseStateUpdate(BaseModel):
    new_state: str = Field(description='目标状态', examples=['in_progress'])


class VulnCaseStateResponse(BaseModel):
    case_id: int = Field(description='漏洞Case ID', examples=[123])
    state: str = Field(description='更新后的状态', examples=['in_progress'])


def _severity_from_risk(risk_score: float) -> str:
    if risk_score >= 9.0:
        return "critical"
    if risk_score >= 7.0:
        return "high"
    if risk_score >= 4.0:
        return "medium"
    return "low"


class VulnCaseListItem(BaseModel):
    case_id: int
    tenant_id: str
    asset_id: int
    risk_score: float
    state: str
    owner: str | None
    sla_due_at: datetime | None
    created_at: datetime | None = None
    title: str = ""
    target: str = ""
    severity: str = "low"


class VulnCaseListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[VulnCaseListItem]


class VulnCaseAssignRequest(BaseModel):
    owner: str = Field(min_length=1, max_length=128)
    sla_due_at: datetime | None = None


class VulnCaseAssignResponse(BaseModel):
    case_id: int
    owner: str
    sla_due_at: datetime | None
