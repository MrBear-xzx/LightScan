# M3 任务13（任务重试历史分页）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 提供任务重试历史查询接口，便于运维审计重试行为。

**Architecture:** 新增 `GET /api/v1/jobs/retries`，基于 `job_retry_requested` 事件分页返回重试记录（源任务ID、新任务ID、类型、重试次数、时间）。

**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：重试历史分页返回结构与字段校验。
2. 扩展 jobs schema（历史项与分页响应）。
3. 实现 retries 路由查询与分页。
4. 全量回归验证并更新文档。
