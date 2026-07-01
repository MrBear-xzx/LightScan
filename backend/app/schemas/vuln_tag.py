from pydantic import BaseModel, Field


class VulnTagCreate(BaseModel):
    tenant_id: str = Field(default='default', description='????')
    name: str = Field(min_length=1, description='????')
    color: str = Field(default='#1890ff', description='????')
    description: str = Field(default='', description='????')


class VulnTagResponse(BaseModel):
    tag_id: int
    tenant_id: str
    name: str
    color: str
    description: str


class VulnTagListResponse(BaseModel):
    tenant_id: str
    total: int
    items: list[VulnTagResponse]


class VulnCaseTagAssignRequest(BaseModel):
    case_id: int = Field(description='????ID')
    tag_ids: list[int] = Field(description='??ID??')
