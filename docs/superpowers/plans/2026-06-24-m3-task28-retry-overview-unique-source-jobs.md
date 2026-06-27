# M3 任务28（重试总览唯一源任务数）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为重试总览增加源任务去重计数，辅助判断重试是否集中在少数任务。
**Architecture:** 扩展 `GET /api/v1/jobs/retries/overview` 返回 `unique_source_jobs`，基于过滤后重试事件 `reference_id` 去重计数。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：总览返回 `unique_source_jobs`。
2. 新增失败测试：同一 `reference_id` 多次重试只计 1。
3. 扩展 schema：新增 `unique_source_jobs` 字段。
4. 扩展 overview 路由：按过滤结果统计去重源任务数。
5. 运行定向测试与全量回归，更新 README。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 返回 `unique_source_jobs`。
- [ ] 重复 `reference_id` 仅计一次。
- [ ] 与 `job_type`/时间窗口过滤保持一致口径。
- [ ] 定向测试与全量测试通过。
