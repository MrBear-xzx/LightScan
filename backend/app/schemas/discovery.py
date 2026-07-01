from pydantic import BaseModel, Field


class DiscoveryTaskCreate(BaseModel):
    tenant_id: str = Field(default='default', description='租户标识', examples=['t1'])
    targets: list[str] = Field(
        min_length=1,
        description='发现目标列表（域名或IP）',
        examples=[['example.com', '198.51.100.10']],
    )
    policy_id: str = Field(default='default-external', description='策略标识', examples=['default-external'])


class DiscoveryTaskResponse(BaseModel):
    task_id: int = Field(description='任务ID', examples=[1])
    tenant_id: str = Field(default='default', description='租户标识', examples=['t1'])
    task_type: str = Field(description='任务类型', examples=['discover'])
    status: str = Field(description='任务状态', examples=['pending'])
