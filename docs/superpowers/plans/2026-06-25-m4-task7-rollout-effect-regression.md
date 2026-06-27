# M4 任务7（rollout 生效回归保护）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 确保插件 rollout 策略更新后，插件列表与健康统计结果同步生效。  
**Architecture:** 为 `/api/v1/plugins` 与 `/api/v1/plugins/health` 引入租户参数读取，按租户策略构建 registry，新增回归测试验证策略生效链路。  
**Tech Stack:** FastAPI、pytest

---

## 任务拆解

1. 新增失败测试：策略更新后 enabled 列表变化正确。  
2. 新增失败测试：策略更新后健康统计与 enabled 列表一致。  
3. 修复 plugins 列表/健康接口读取租户策略逻辑。  
4. 更新 README 说明。  
5. 运行定向测试与全量回归。

## 验收标准

- [ ] 策略更新后 `/api/v1/plugins?tenant_id=...&status=enabled` 返回符合预期。  
- [ ] 策略更新后 `/api/v1/plugins/health?tenant_id=...` 统计结果正确。  
- [ ] 定向测试与全量测试通过。
