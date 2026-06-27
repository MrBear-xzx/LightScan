from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class JobStatusResponse(BaseModel):
    tenant_id: str
    job_id: str
    job_type: str
    status: str
    updated_at: datetime
    last_error: str | None = None
    retry_count: int | None = None
    last_retry_at: str | None = None


class JobRetryRequest(BaseModel):
    tenant_id: str
    job_id: str


class JobRetryResponse(BaseModel):
    tenant_id: str
    source_job_id: str
    new_job_id: str
    job_type: str
    status: str


class JobRetryHistoryItem(BaseModel):
    job_id: str
    new_job_id: str
    job_type: str
    retry_count: int
    requested_at: datetime


class JobRetryHistoryResponse(BaseModel):
    tenant_id: str
    page: int
    page_size: int
    total: int
    items: list[dict[str, Any]]


class JobRetryPolicyUpsertRequest(BaseModel):
    tenant_id: str
    max_retry_count: int = Field(default=3, ge=1, le=20)
    retry_cooldown_seconds: int = Field(default=60, ge=0, le=3600)


class JobRetryPolicyResponse(BaseModel):
    tenant_id: str
    max_retry_count: int
    retry_cooldown_seconds: int


class JobRetryHistoryOverviewResponse(BaseModel):
    tenant_id: str
    total_retries: int
    unique_source_jobs: int
    job_type_counts: dict[str, int]
    retry_count_distribution: dict[str, int]
    max_retry_count: int
    avg_retry_count: float
    latest_retry_count: int
    latest_retry_job_type: str | None = None
    latest_source_job_id: str | None = None
    first_retry_requested_at: str | None = None
    last_retry_requested_at: str | None = None
