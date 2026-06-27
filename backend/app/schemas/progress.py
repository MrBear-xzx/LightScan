from pydantic import BaseModel, Field


class ScanTaskProgressItem(BaseModel):
    task_id: int = Field(description="任务ID")
    target: str = Field(default="", description="目标")
    findings_count: int = Field(default=0, description="发现数")
    task_type: str = Field(description="任务类型", examples=["discover"])
    status: str = Field(description="状态", examples=["pending", "running", "completed", "failed"])
    worker_id: str | None = Field(default=None, description="工作节点ID")
    started_at: str | None = Field(default=None, description="开始时间")
    ended_at: str | None = Field(default=None, description="结束时间")


class BatchProgressResponse(BaseModel):
    tenant_id: str
    batch_id: str | None = None
    total: int
    completed: int
    failed: int
    running: int
    pending: int
    tasks: list[ScanTaskProgressItem]
