# M9 任务2（日志聚合与采集）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供操作日志查询接口，基于 events 表支持分页与事件类型过滤，便于日志采集系统集成。  
**Architecture:** 新增 /api/v1/ops/logs 端点，复用 events 表。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：OperationLogItem、OperationLogResponse。
2. 新增 operation_log_service：基于 events 表的分页日志查询。
3. 新增路由：GET /api/v1/ops/logs。
4. 注册到 main.py。
5. 新增测试：空数据、正常返回、事件类型过滤。
6. 更新 README。

## 验收标准

- [ ] GET /api/v1/ops/logs 支持分页与 event_type 过滤。
- [ ] 返回操作日志列表与总数。
- [ ] 定向测试通过。
