# M3 任务19（任务重试历史排序方向）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为重试历史接口增加排序方向参数，支持按时间升序/降序返回记录。
**Architecture:** 在 `GET /api/v1/jobs/retries` 新增 `sort_order=asc|desc` 参数，默认保持现有降序（最新优先）；查询层按 `event_id` 应用方向排序，其他筛选与分页逻辑保持不变。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：`sort_order=asc` 场景按最早事件优先返回。
2. 扩展 retries 路由参数与排序实现（`asc/desc`）。
3. 运行定向测试与全量回归。
4. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries` 支持 `sort_order=asc|desc`。
- [ ] 默认仍为 `desc`，保持兼容。
- [ ] 与分页、关键字、类型、时间筛选可组合使用。
- [ ] 定向测试与全量测试通过。
