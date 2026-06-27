from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    tenant_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(default='')


class ProjectResponse(BaseModel):
    project_id: int
    tenant_id: str
    name: str
    description: str


class ProjectListResponse(BaseModel):
    tenant_id: str
    total: int
    items: list[ProjectResponse]


class ProjectMemberAdd(BaseModel):
    user_id: int
    role: str = Field(default='member', pattern='^(admin|member|viewer)$')


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: str
