from pydantic import BaseModel


class OperationLogItem(BaseModel):
    event_id: int
    tenant_id: str
    event_type: str
    reference_id: str
    payload: dict
    created_at: str


class OperationLogResponse(BaseModel):
    tenant_id: str
    page: int
    page_size: int
    total: int
    items: list[OperationLogItem]
