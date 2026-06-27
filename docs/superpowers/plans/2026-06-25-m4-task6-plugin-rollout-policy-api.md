# M4 任务6（插件 rollout 策略 API）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 提供插件 rollout 策略的租户级查询与更新接口，并记录审计事件。  
**Architecture:** 复用 `policies` 表存储 `plugin_rollout` 配置，新增 `GET/PUT /api/v1/plugins/rollout-policy`，更新时写入 `plugin_rollout_policy_updated` 事件。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：rollout 策略可查询与更新。  
2. 新增失败测试：策略更新写入审计事件。  
3. 新增 schema：rollout 策略请求/响应模型。  
4. 新增 service：策略读写能力。  
5. 扩展 plugins 路由：新增 `GET/PUT /rollout-policy`。  
6. 更新 README 说明。  
7. 运行定向测试与全量回归。

## 验收标准

- [ ] `GET /api/v1/plugins/rollout-policy` 可返回租户配置（无配置回退默认）。  
- [ ] `PUT /api/v1/plugins/rollout-policy` 可持久化并返回配置。  
- [ ] 策略更新写入 `plugin_rollout_policy_updated` 事件。  
- [ ] 定向测试与全量测试通过。
