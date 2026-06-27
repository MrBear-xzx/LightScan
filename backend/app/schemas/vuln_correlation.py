from pydantic import BaseModel


class VulnCaseSummary(BaseModel):
    case_id: int
    risk_score: float
    state: str
    owner: str | None
    created_at: str


class AssetCorrelationItem(BaseModel):
    asset_id: int
    total_cases: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    top_risk_case: VulnCaseSummary | None


class VulnCorrelationResponse(BaseModel):
    tenant_id: str
    total_assets: int
    total_cases: int
    items: list[AssetCorrelationItem]
