# M9 任务3（告警规则配置）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供可配置的告警规则管理，基于 policy 表持久化，支持指标阈值触发。  
**Architecture:** 基于 policy 表（alert_rule_ 前缀），提供 CRUD 接口。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：AlertRuleMetric、AlertRuleConfig、AlertRuleResponse、AlertRuleListResponse。
2. 新增 alert_rule_service：基于 policy 表的 CRUD。
3. 新增路由：GET/POST/DELETE /api/v1/ops/alert-rules。
4. 注册到 main.py。
5. 新增测试：空列表、CRUD、删除不存在。
6. 更新 README。

## 验收标准

- [ ] 告警规则支持指标、运算符、阈值、持续时间的配置。
- [ ] CRUD 接口完整可用。
- [ ] 定向测试通过。
