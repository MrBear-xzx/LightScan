# M3 任务16（任务状态详情增强）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强 `GET /api/v1/jobs/status` 返回信息，补充失败任务排障所需的错误与重试元数据。
**Architecture:** 在现有状态查询逻辑上复用失败事件 payload，新增响应字段 `last_error/retry_count/last_retry_at`；仅在 `failed` 状态下返回这些字段，其余状态返回空值。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：失败任务状态返回 `last_error/retry_count/last_retry_at`。
2. 扩展状态响应 schema：增加失败元信息字段（可空）。
3. 扩展 status 路由：读取失败事件 payload 并映射到响应字段。
4. 运行定向测试与全量测试。
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/status` 在失败任务下返回 `last_error/retry_count/last_retry_at`。
- [ ] 其他状态返回结构兼容，不破坏现有调用方。
- [ ] 定向测试与全量测试通过。
