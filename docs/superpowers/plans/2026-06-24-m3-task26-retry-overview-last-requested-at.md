# M3 任务26（重试总览最近重试时间）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为重试总览接口补充最近一次重试时间，便于看板展示数据新鲜度。
**Architecture:** 扩展 `GET /api/v1/jobs/retries/overview` 返回 `last_retry_requested_at`，从过滤后的 `job_retry_requested` 事件中取最新 `created_at`；无数据时返回 `null`。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：overview 返回 `last_retry_requested_at`。
2. 扩展 schema：增加 `last_retry_requested_at` 可空字段。
3. 扩展 overview 路由：聚合时计算过滤结果中的最新事件时间。
4. 运行定向测试与全量回归。
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 返回 `last_retry_requested_at`。
- [ ] 该时间与过滤条件一致（按过滤后的结果计算）。
- [ ] 无匹配记录时返回 `null`。
- [ ] 定向测试与全量测试通过。
