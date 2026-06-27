# M3 任务31（重试总览最近源任务）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在重试总览中补充最近一次重试对应的源任务 ID，便于快速定位问题任务。
**Architecture:** 扩展 `GET /api/v1/jobs/retries/overview` 返回 `latest_source_job_id`；与 `last_retry_requested_at/latest_retry_count/latest_retry_job_type` 绑定同一条最近事件。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：overview 返回 `latest_source_job_id`。
2. 扩展 schema：增加 `latest_source_job_id` 可空字段。
3. 扩展 overview 路由：在记录最近事件时同步保存 `reference_id`。
4. 运行定向测试与全量回归。
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 返回 `latest_source_job_id`。
- [ ] 该字段与最近事件的时间/计数/类型一致。
- [ ] 无匹配数据时返回 `null`。
- [ ] 定向测试与全量测试通过。
