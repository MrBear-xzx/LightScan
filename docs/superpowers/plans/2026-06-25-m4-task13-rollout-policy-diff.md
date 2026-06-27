# M4 任务13（rollout 策略变更 diff 输出）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为插件 rollout 策略更新接口补充“变更前后差异”输出，降低策略变更排查成本。  
**Architecture:** 在 `PUT /api/v1/plugins/rollout-policy` 中读取更新前策略，与更新后策略做逐插件比对，仅输出有变化的插件项，并将 diff 一并写入审计事件。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：二次更新策略时，响应应包含目标插件的 `before/after` 差异。  
2. 扩展 schema：新增 rollout 策略更新响应模型，包含 `diff` 字段。  
3. 扩展路由：在 upsert 前读取旧策略，upsert 后计算差异并返回。  
4. 扩展审计：策略更新事件 payload 增加 `diff`，便于审计回放。  
5. 更新 README：补充 rollout-policy 接口 diff 能力说明。  
6. 运行定向测试与全量回归测试。

## 验收标准

- [ ] `PUT /api/v1/plugins/rollout-policy` 响应包含 `diff` 字段。  
- [ ] `diff` 仅包含发生变更的插件项，且每项包含 `before/after`。  
- [ ] rollout 审计事件 payload 包含 `diff` 信息。  
- [ ] 定向测试与全量测试通过。
