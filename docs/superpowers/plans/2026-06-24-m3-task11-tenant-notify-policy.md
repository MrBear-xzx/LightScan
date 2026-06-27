# M3 任务11（租户通知策略持久化）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将通知去重策略持久化到租户级配置，减少每次请求显式传参成本。

**Architecture:** 新增策略接口 `GET/PUT /api/v1/notifications/policy` 读写 `policies` 表中 `name=notification` 配置；通知派发在请求未提供去重参数时回退读取租户策略。

**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增策略读写 API 与测试（upsert + query）。
2. 派发接口接入租户策略回退逻辑。
3. 保持兼容：请求显式传参优先于租户默认策略。
4. 执行全量回归并更新文档。
