# M5 任务4（扫描任务取消与超时检测）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供扫描任务取消与超时检测能力，使扫描任务可管理。  
**Architecture:** 新增两个端点：POST /api/v1/scan/{task_id}/cancel（手动取消）、POST /api/v1/scan/timeout-check（超时检测）。  
**Tech Stack:** FastAPI、SQLAlchemy、pytest

## 任务拆解

1. 新增 task_control_service：取消任务（改 status + 记录事件）与超时检查（按创建时间筛选超时任务）。
2. 新增路由：cancel 端点与 timeout-check 端点。
3. 新增测试：取消不存在任务返回404、取消成功、重复取消、超时检查。
4. 更新 README。

## 验收标准

- [ ] POST /api/v1/scan/{task_id}/cancel 标记任务为 cancelled。
- [ ] 不可重复取消已终结的任务。
- [ ] POST /api/v1/scan/timeout-check 标记超时任务为 timeout。
- [ ] 定向测试通过。
