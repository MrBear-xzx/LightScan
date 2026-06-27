# M4 任务4（插件启停与灰度配置基座）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 提供插件启停与灰度的最小配置驱动能力，为后续插件管理中心打底。  
**Architecture:** 新增插件 rollout 配置模块（`status` + `rollout`），注册中心按配置构建元信息，插件列表支持状态过滤，健康接口默认统计启用插件。  
**Tech Stack:** FastAPI、pytest

---

## 任务拆解

1. 新增失败测试：插件列表支持 `status=enabled`。  
2. 新增失败测试：插件列表支持 `status=disabled`。  
3. 新增失败测试：健康接口仅统计启用插件。  
4. 新增 rollout 配置模块。  
5. 注册中心接入 rollout 配置并暴露 `rollout` 字段。  
6. 更新 plugins 路由过滤逻辑。  
7. 更新 README 说明。  
8. 运行定向测试与全量回归。

## 验收标准

- [ ] 插件列表支持 `status` 过滤。  
- [ ] 插件列表返回 `rollout` 字段。  
- [ ] 健康接口默认只统计 `enabled` 插件。  
- [ ] 定向测试与全量测试通过。
