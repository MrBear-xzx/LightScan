# M3 任务15（任务重试策略可配置）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为异步任务重试护栏提供租户级可配置能力，支持按租户调整最大重试次数与重试冷却时间。
**Architecture:** 复用 `policies` 表新增 `jobs_retry` 策略项；新增 `GET/PUT /api/v1/jobs/retry-policy` 管理接口；`POST /api/v1/jobs/retry` 在执行护栏判断时优先读取租户策略，缺省回退到默认值（3 次 / 60 秒）。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：重试策略接口可设置/查询。
2. 新增失败测试：重试接口可按租户策略覆盖默认护栏。
3. 新增策略服务：`get_job_retry_policy` / `upsert_job_retry_policy`。
4. 扩展 jobs 路由：新增 `GET/PUT /retry-policy`，并将重试护栏切换为策略驱动。
5. 回归验证：定向测试 + 全量测试 + README 更新。

## 验收标准

- [ ] `GET /api/v1/jobs/retry-policy` 返回租户重试策略（无配置时回退默认值）。
- [ ] `PUT /api/v1/jobs/retry-policy` 可持久化 `max_retry_count/retry_cooldown_seconds`。
- [ ] `POST /api/v1/jobs/retry` 使用租户策略执行护栏判断。
- [ ] 定向测试与全量测试通过。
