# M3 任务14（任务重试历史筛选能力）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强 `GET /api/v1/jobs/retries`，支持按任务类型与时间窗口筛选重试历史，提升排障与审计效率。
**Architecture:** 在现有 `job_retry_requested` 事件基础上扩展查询参数，不改动表结构。接口新增 `job_type/requested_from/requested_to` 过滤，并在时间窗口非法时返回 400。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：覆盖 `job_type` 与时间窗口筛选行为。
2. 新增失败测试：覆盖时间窗口非法（from > to）的错误处理。
3. 扩展 jobs 路由：新增筛选参数、时间窗口校验、筛选后分页返回。
4. 执行回归：定向测试 + 全量测试。
5. 更新 README 能力说明，补充新筛选参数。

## 验收标准

- [ ] `GET /api/v1/jobs/retries` 支持 `job_type=notification|ticket_sync` 筛选。
- [ ] `GET /api/v1/jobs/retries` 支持 `requested_from/requested_to` 时间窗口筛选。
- [ ] 当 `requested_from > requested_to` 时返回 `400` 与明确信息。
- [ ] 定向测试与全量测试通过。
