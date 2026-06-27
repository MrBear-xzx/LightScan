# M4 任务1（插件管理基础能力）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立插件管理最小可用能力，支持查看插件列表与健康状态。  
**Architecture:** 在现有插件运行时基础上补齐 `health` 契约、增强注册中心元信息，并新增插件管理 API。  
**Tech Stack:** FastAPI、pytest

---

## 任务拆解

1. 新增失败测试：`GET /api/v1/plugins` 返回内置插件。  
2. 新增失败测试：插件列表支持 `capability` 过滤。  
3. 新增失败测试：`GET /api/v1/plugins/health` 返回健康统计。  
4. 插件契约补齐 `health`。  
5. 注册中心增加元信息与默认内置插件构建。  
6. 新增 `plugins` 路由并挂载到主应用。  
7. 更新 README 能力说明。  
8. 运行定向测试与全量回归。

## 验收标准

- [ ] 插件列表接口可返回内置 `http_probe` 与 `nuclei_json`。  
- [ ] 列表接口支持按能力过滤。  
- [ ] 插件健康接口返回 `total/healthy/items`。  
- [ ] 定向测试与全量测试通过。
