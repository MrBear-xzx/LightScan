# M3 任务9（异步任务状态查询）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 提供异步任务状态查询接口，支持前端或运维按 `job_id` 查询队列任务当前状态。

**Architecture:** 新增 `GET /api/v1/jobs/status`，基于 events 表中 `*_queued/*_finished/*_failed` 事件推导状态；并补齐 worker 成功完成事件写入。

**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：验证 queued/success/failed 三种状态查询结果。
2. 新增 jobs 路由与 schema。
3. worker 成功路径补充 finished 事件。
4. 接口注册、全量测试与文档更新。
