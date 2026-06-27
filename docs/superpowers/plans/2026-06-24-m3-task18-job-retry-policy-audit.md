# M3 任务18（任务重试策略变更审计）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为任务重试策略配置增加审计留痕，确保策略变更可追溯。
**Architecture:** 在 `PUT /api/v1/jobs/retry-policy` 成功写入策略后，追加写入 `job_retry_policy_updated` 事件，事件 payload 保存当前策略值（`max_retry_count/retry_cooldown_seconds`）。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：更新重试策略后，存在 `job_retry_policy_updated` 事件。
2. 扩展 jobs 策略接口：策略更新后记录审计事件并提交事务。
3. 运行定向测试与全量回归。
4. 更新 README 审计说明。

## 验收标准

- [ ] 更新任务重试策略后，`events` 表有 `job_retry_policy_updated` 记录。
- [ ] 事件 payload 包含最新策略字段值。
- [ ] 定向测试与全量测试通过。
