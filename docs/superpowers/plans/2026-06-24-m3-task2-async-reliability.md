# M3 任务2（异步可靠性基线）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将通知派发与工单同步升级为“可异步入队”的接口，返回 job_id 并提供最小重试基线。

**Architecture:** 新增 workers 异步任务函数，API 支持 `mode=sync|async`。`async` 模式下只入队并返回任务ID；`sync` 模式保持兼容。

**Tech Stack:** FastAPI、Celery、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：通知/工单 `mode=async` 返回 job_id。
2. 实现 Celery 任务：`dispatch_notification_job`、`ticket_sync_job`。
3. 路由接入：dispatch/sync 支持异步模式。
4. 更新 README 与全量测试。
