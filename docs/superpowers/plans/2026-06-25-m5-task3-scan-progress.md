# M5 任务3（扫描任务进度查询）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供扫描任务进度查询接口，支持按批次ID或任务ID列表批量查询任务状态。  
**Architecture:** 新增 GET /api/v1/scan/progress，从 scan_tasks 表按 task_ids 或 event 记录中的 task_ids 查询状态分布。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：ScanTaskProgressItem、BatchProgressResponse。
2. 新增 progress_service：支持 task_ids 或 batch_id 两个查询维度。
3. 在 batch_scan 事件 payload 中增加 task_ids 字段，便于 batch_id 回查。
4. 新增 route：GET /api/v1/scan/progress。
5. 新增测试：无批次返回空、未知批次返回空、task_ids 查询。
6. 更新 README。

## 验收标准

- [ ] GET /api/v1/scan/progress 支持 batch_id 与 task_ids 参数。
- [ ] 无匹配批次返回空任务列表。
- [ ] 返回包括 completed/failed/running/pending 分布统计。
