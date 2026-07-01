from pydantic import BaseModel, Field


class BatchScanTarget(BaseModel):
    targets: list[str] = Field(
        min_length=1,
        description='??????????IP?',
        examples=[['example.com', '10.0.0.1']],
    )
    policy_id: str = Field(description='????', examples=['default-external'])


class BatchScanRequest(BaseModel):
    tenant_id: str = Field(default='default', description='????', examples=['t1'])
    batches: list[BatchScanTarget] = Field(
        min_length=1,
        description='??????????????????+???',
    )


class BatchScanTaskItem(BaseModel):
    task_id: int = Field(description='??ID')
    tenant_id: str = Field(description='????')
    targets: list[str] = Field(description='????????')
    policy_id: str = Field(description='????')
    status: str = Field(description='????')


class BatchScanResponse(BaseModel):
    batch_id: str = Field(description='????', examples=['batch-20260625-xxxx'])
    tenant_id: str = Field(description='????')
    total: int = Field(description='?????')
    succeeded: int = Field(description='?????')
    failed: int = Field(description='???')
    tasks: list[BatchScanTaskItem] = Field(description='????')
    errors: list[str] = Field(default_factory=list, description='??????')
