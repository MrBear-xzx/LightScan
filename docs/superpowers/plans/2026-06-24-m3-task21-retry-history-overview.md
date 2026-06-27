# M3 任务21（任务重试历史总览）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增任务重试历史总览接口，提供聚合指标供看板快速展示。
**Architecture:** 新增 `GET /api/v1/jobs/retries/overview`，基于 `job_retry_requested` 事件聚合总重试次数与按任务类型计数；支持时间窗口过滤以对齐列表/导出接口的统计口径。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：总览接口返回 `total_retries` 与 `job_type_counts`。
2. 新增 schema：重试历史总览响应模型。
3. 新增路由：聚合 `job_retry_requested` 事件并返回统计结果。
4. 复用时间窗口参数校验（`requested_from <= requested_to`）。
5. 运行定向测试与全量回归，更新 README。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 返回 `total_retries`。
- [ ] 返回 `job_type_counts`，至少包含 `notification/ticket_sync`。
- [ ] 支持 `requested_from/requested_to` 时间窗口过滤。
- [ ] 定向测试与全量测试通过。
