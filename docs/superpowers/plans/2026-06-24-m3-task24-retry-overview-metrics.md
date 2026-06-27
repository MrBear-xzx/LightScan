# M3 任务24（重试总览增强指标）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强重试总览接口，提供更具诊断价值的重试强度指标。
**Architecture:** 在 `GET /api/v1/jobs/retries/overview` 现有统计基础上新增 `max_retry_count` 与 `avg_retry_count`；从 `job_retry_requested` 事件 payload 的 `retry_count` 聚合计算，空数据时返回 `0/0.0`。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：总览接口返回 `max_retry_count`、`avg_retry_count`。
2. 扩展 schema：增加新指标字段。
3. 扩展 overview 路由：聚合计算最大值与平均值（保留两位小数）。
4. 运行定向测试与全量回归。
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 返回 `max_retry_count`。
- [ ] 返回 `avg_retry_count`（两位小数）。
- [ ] 与现有 `total_retries/job_type_counts` 同时可用。
- [ ] 定向测试与全量测试通过。
