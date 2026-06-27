# M3 任务5（异步链路可观测增强）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为异步通知与异步工单链路补齐最小可观测能力，支持运维快速判断“是否成功入队”。

**Architecture:** 在异步路由分支记录入队事件（`notification_async_queued`、`ticket_sync_async_queued`），并在 `/metrics` 暴露对应计数器指标。

**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：异步入队后应写入队列事件，并在 `/metrics` 暴露新计数器。
2. 通知异步分支记录 `notification_async_queued` 事件。
3. 工单异步分支记录 `ticket_sync_async_queued` 事件。
4. 指标接口新增两个 async queued 计数器并更新文档与全量测试。
