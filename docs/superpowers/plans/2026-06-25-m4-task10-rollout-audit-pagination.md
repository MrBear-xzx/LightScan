# M4 任务10（rollout 审计分页）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 rollout 审计接口增加分页能力，支持在审计事件增多后稳定查询。  
**Architecture:** 扩展审计响应 schema 增加 `page/page_size/total`，service 层增加总数统计与分页查询，路由新增分页参数。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：rollout 审计支持 `page/page_size`。  
2. 扩展 schema：审计响应新增分页字段。  
3. 扩展 service：新增总数统计与分页查询函数。  
4. 扩展路由：新增分页参数并返回总数。  
5. 更新 README 审计能力说明。  
6. 运行定向测试与全量回归。

## 验收标准

- [ ] `GET /api/v1/plugins/rollout-audit` 支持 `page/page_size` 参数。  
- [ ] 响应包含 `page/page_size/total/items`。  
- [ ] 分页结果顺序稳定（按 event_id 倒序）。  
- [ ] 定向测试与全量测试通过。
