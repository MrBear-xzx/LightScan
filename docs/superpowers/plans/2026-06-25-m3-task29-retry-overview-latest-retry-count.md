# M3 任务29（重试总览最近重试计数）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在重试总览中增加最近一次重试计数，快速评估当前重试深度。
**Architecture:** 扩展 `GET /api/v1/jobs/retries/overview` 返回 `latest_retry_count`，取过滤后最近一条重试事件的 `retry_count`；无数据时返回 `0`。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：overview 返回 `latest_retry_count`。
2. 扩展 schema：增加 `latest_retry_count` 字段。
3. 扩展 overview 路由：在确定 `last_retry_requested_at` 的同时记录其 `retry_count`。
4. 运行定向测试与全量回归。
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 返回 `latest_retry_count`。
- [ ] 数值与 `last_retry_requested_at` 对应记录一致。
- [ ] 无匹配记录时返回 `0`。
- [ ] 定向测试与全量测试通过。
