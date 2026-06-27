from pydantic import BaseModel


class VulnSummaryCounts(BaseModel):
    new: int
    confirmed: int
    in_progress: int
    fixed: int
    ignored: int
    reopened: int


class VulnSummaryResponse(BaseModel):
    tenant_id: str
    counts: VulnSummaryCounts


class OwnerSlaStats(BaseModel):
    total_cases: int
    overdue_cases: int


class SlaOverviewStatusCounts(BaseModel):
    new: int
    confirmed: int
    in_progress: int
    fixed: int
    ignored: int
    reopened: int


class SlaOverviewResponse(BaseModel):
    tenant_id: str
    total_cases: int
    overdue_cases: int
    due_48h_cases: int
    no_sla_cases: int
    status_counts: SlaOverviewStatusCounts
    owner_breakdown: dict[str, OwnerSlaStats]


class SlaTrendPoint(BaseModel):
    date: str
    overdue_cases: int
    total_cases: int


class SlaTrendResponse(BaseModel):
    tenant_id: str
    days: int
    granularity: str
    points: list[SlaTrendPoint]
