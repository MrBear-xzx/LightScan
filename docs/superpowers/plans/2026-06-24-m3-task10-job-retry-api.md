# M3 任务10（异步任务失败重试控制面）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 提供最小可用的失败任务手动重试能力，支持按 `job_id` 重新入队。

**Architecture:** 新增 `POST /api/v1/jobs/retry`，读取失败事件 payload 重新调用对应异步任务；记录 `job_retry_requested` 与新的 queued 事件。

**Tech Stack:** FastAPI、Celery、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：失败任务应可通过 API 重试并返回新 job_id。
2. 扩展 jobs schema（重试请求/响应）。
3. 实现 retry 路由：按失败事件类型重入队通知或工单任务。
4. 补充失败事件 payload 字段，确保重试参数可还原并执行全量回归。
