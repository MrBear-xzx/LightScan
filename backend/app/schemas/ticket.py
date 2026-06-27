from pydantic import BaseModel, Field


class TicketSyncRequest(BaseModel):
    tenant_id: str
    provider: str
    case_ids: list[int]
    mode: str = Field(default='sync', pattern='^(sync|async)$')


class TicketSyncResponse(BaseModel):
    tenant_id: str
    provider: str
    mode: str
    job_id: str | None = None
    synced: int
