from pydantic import BaseModel, Field


class ScanPolicyRule(BaseModel):
    plugin_id: str = Field(description='??ID')
    enabled: bool = Field(default=True, description='????')
    config: dict = Field(default_factory=dict, description='??????')


class ScanPolicyCreate(BaseModel):
    tenant_id: str = Field(default='default', description='????')
    name: str = Field(min_length=1, description='????')
    description: str = Field(default='', description='????')
    plugins: list[ScanPolicyRule] = Field(default_factory=list, description='????')
    extra_config: dict = Field(default_factory=dict, description='????????????')


class ScanPolicyResponse(BaseModel):
    tenant_id: str
    name: str
    description: str
    plugins: list[ScanPolicyRule]
    extra_config: dict


class ScanPolicyListResponse(BaseModel):
    tenant_id: str
    total: int
    items: list[ScanPolicyResponse]
