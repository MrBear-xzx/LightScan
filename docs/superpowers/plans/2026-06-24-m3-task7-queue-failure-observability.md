# M3 任务7（队列失败可观测增强）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为异步任务失败建立统一事件与指标，支持快速发现和定位任务失败。

**Architecture:** 在通知/工单异步 worker 的异常路径记录标准化失败事件（`notification_async_failed`、`ticket_sync_async_failed`），并在 `/metrics` 暴露对应失败计数器。

**Tech Stack:** Celery、FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：模拟 worker 异常后应写入失败事件。
2. worker 失败路径记录标准化失败事件与错误类型信息。
3. 指标接口新增 async failed 计数器。
4. 扩展指标测试与全量回归验证。
