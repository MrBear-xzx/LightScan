# M4 任务3（插件健康观测指标）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将插件健康状态纳入 `/metrics`，支持运维侧统一观测。  
**Architecture:** 复用插件注册中心与 `health()` 契约，在指标导出时聚合插件总数、健康数、异常数。  
**Tech Stack:** FastAPI、pytest

---

## 任务拆解

1. 新增失败测试：`/metrics` 包含插件健康指标名。  
2. 新增失败测试：默认内置插件场景下指标值正确。  
3. 扩展 metrics 路由聚合逻辑。  
4. 更新 README 指标说明。  
5. 运行定向测试与全量回归。

## 验收标准

- [ ] `/metrics` 返回 `lightscan_plugins_total`。  
- [ ] `/metrics` 返回 `lightscan_plugins_healthy_total`。  
- [ ] `/metrics` 返回 `lightscan_plugins_unhealthy_total`。  
- [ ] 定向测试与全量测试通过。
