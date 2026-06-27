# M4 任务9（插件 rollout 治理增强）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强插件 rollout 策略治理能力，补齐策略输入校验与审计查询。  
**Architecture:** 在现有 rollout policy API 基础上新增未知插件校验，并新增 rollout 审计查询接口。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：未知插件写入策略返回 400。  
2. 新增失败测试：rollout 审计查询接口可返回最新事件。  
3. 实现策略白名单校验。  
4. 实现 `GET /api/v1/plugins/rollout-audit`。  
5. 扩展 schema 支持审计响应模型。  
6. 更新 README。  
7. 运行定向测试与全量回归。

## 验收标准

- [ ] 未知插件写入策略被拒绝并返回明确错误。  
- [ ] rollout 审计接口可按租户返回最近策略变更。  
- [ ] 定向测试与全量测试通过。
