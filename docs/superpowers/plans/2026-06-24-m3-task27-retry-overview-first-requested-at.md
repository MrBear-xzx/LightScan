# M3 任务27（重试总览最早重试时间）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在重试总览中补充最早重试时间，形成完整时间边界（最早/最近）。
**Architecture:** 扩展 `GET /api/v1/jobs/retries/overview` 返回 `first_retry_requested_at`，按过滤后的匹配记录计算最早 `created_at`；无匹配数据时返回 `null`。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：overview 返回 `first_retry_requested_at`。
2. 扩展 schema：增加 `first_retry_requested_at` 可空字段。
3. 扩展 overview 路由：在聚合时计算最早重试时间。
4. 运行定向测试与全量回归。
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 返回 `first_retry_requested_at`。
- [ ] 时间值基于过滤后的匹配记录计算。
- [ ] 无数据时返回 `null`。
- [ ] 定向测试与全量测试通过。
