from pydantic import BaseModel, Field


class BackupRecord(BaseModel):
    backup_id: str = Field(description='??ID')
    tenant_id: str
    created_at: str = Field(description='????')
    size_bytes: int = Field(default=0, description='????')
    status: str = Field(description='??', examples=['completed', 'failed', 'in_progress'])
    description: str = Field(default='', description='????')


class BackupListResponse(BaseModel):
    tenant_id: str
    total: int
    items: list[BackupRecord]


class BackupCreateResponse(BaseModel):
    tenant_id: str
    backup_id: str
    status: str
    message: str
