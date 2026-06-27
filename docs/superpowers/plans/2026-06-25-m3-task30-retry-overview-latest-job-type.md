# M3 任务30（重试总览最近重试任务类型）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在重试总览中增加最近一次重试对应的任务类型，便于快速判断波动来源。
**Architecture:** 扩展 `GET /api/v1/jobs/retries/overview` 返回 `latest_retry_job_type`；与 `last_retry_requested_at/latest_retry_count` 共享同一条最近事件。最近判定采用 `(created_at, event_id)`，避免同秒时间戳下不稳定。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：overview 返回 `latest_retry_job_type`。
2. 扩展 schema：增加 `latest_retry_job_type` 可空字段。
3. 扩展 overview 路由：同步维护最近事件的任务类型，并用 `(created_at, event_id)` 稳定排序。
4. 运行定向测试与全量回归。
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 返回 `latest_retry_job_type`。
- [ ] 该字段与 `last_retry_requested_at/latest_retry_count` 对应同一事件。
- [ ] 同时间戳场景结果稳定（按 `event_id` 断平）。
- [ ] 定向测试与全量测试通过。
