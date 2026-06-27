# M5 任务5（扫描策略模板）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供扫描策略模板管理能力，支持创建/查询/更新/删除扫描配置模板。  
**Architecture:** 基于现有 policy 表，以 scan_template_ 前缀区分存储，提供 RESTful CRUD。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：ScanPolicyRule、ScanPolicyCreate、ScanPolicyResponse、ScanPolicyListResponse。
2. 新增 scan_policy_service：CRUD 操作，基于 policy 表存储。
3. 新增路由：GET/PUT/DELETE /api/v1/scan/policies。
4. 注册路由到 main.py。
5. 新增测试：空列表、CRUD 全流程、删除不存在返回404。
6. 更新 README。

## 验收标准

- [ ] GET /api/v1/scan/policies 返回策略模板列表。
- [ ] PUT /api/v1/scan/policies 创建或更新策略。
- [ ] GET /api/v1/scan/policies/{name} 返回策略详情。
- [ ] DELETE /api/v1/scan/policies/{name} 删除策略。
- [ ] 定向测试通过。
