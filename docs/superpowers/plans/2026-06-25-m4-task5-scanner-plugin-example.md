# M4 任务5（扫描插件接入示例）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增一个扫描插件接入示例，验证插件扩展路径的低成本接入能力。  
**Architecture:** 新增 `mockx_json` 扫描插件实现 `scan/normalize/health`，接入 rollout 配置与插件注册中心，并补齐服务/API/指标回归测试。  
**Tech Stack:** FastAPI、pytest

---

## 任务拆解

1. 新增失败测试：`mockx_json` 插件标准化输出。  
2. 新增失败测试：插件列表包含 `mockx_json`。  
3. 实现 `mockx_json` 扫描插件。  
4. 接入 rollout 配置与注册中心。  
5. 修正插件健康指标测试为动态断言。  
6. 更新 README 说明。  
7. 运行定向测试与全量回归。

## 验收标准

- [ ] `mockx_json` 插件可通过 `scan/normalize/health` 契约验证。  
- [ ] 插件列表可查询到 `mockx_json`。  
- [ ] 插件健康指标测试不依赖固定插件数量。  
- [ ] 定向测试与全量测试通过。
