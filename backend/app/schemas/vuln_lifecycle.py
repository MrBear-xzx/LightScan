from pydantic import BaseModel, Field


class StateDistribution(BaseModel):
    new: int = Field(description='??', default=0)
    in_progress: int = Field(description='???', default=0)
    resolved: int = Field(description='???', default=0)
    false_positive: int = Field(description='??', default=0)
    rejected: int = Field(description='???', default=0)


class VulnerabilityLifecycleResponse(BaseModel):
    tenant_id: str
    total_open: int = Field(description='????????new+in_progress?')
    total_cases: int = Field(description='???????')
    state_distribution: StateDistribution = Field(description='?????')
    created_today: int = Field(description='????')
    created_this_week: int = Field(description='????')
    resolved_today: int = Field(description='????')
    avg_days_open: float = Field(description='?????????????')
