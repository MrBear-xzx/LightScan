# M3 任务33（重试总览时间窗口口径）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 明确并固化重试总览接口的时间窗口过滤行为，确保与历史列表/导出接口口径一致。  
**Architecture:** 复用 `GET /api/v1/jobs/retries/overview` 已有 `requested_from/requested_to` 参数与校验逻辑，补齐测试与文档说明，不新增表结构。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增测试：总览接口支持时间窗口过滤。  
2. 新增测试：当 `requested_from > requested_to` 返回 400。  
3. 更新 README：补充总览接口支持时间窗口过滤说明。  
4. 运行定向测试与全量回归。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/overview` 在时间窗口过滤下返回正确聚合结果。  
- [ ] 非法时间窗口返回 `400` 且错误信息明确。  
- [ ] README 中总览能力说明与接口行为一致。  
- [ ] 定向测试与全量测试通过。
