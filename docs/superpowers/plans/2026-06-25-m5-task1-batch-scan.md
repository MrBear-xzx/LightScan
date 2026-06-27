# M5 任务1（批量扫描接口）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 为扫描链路增加批量目标提交能力，一次性创建多个独立发现任务并返回批次 ID。  
**Architecture:** 新增 route/POST /api/v1/scan/batch，在现有 discovery_service 基础上按目标组循环创建任务，异常隔离（单个失败不影响其他）。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：BatchScanRequest（租户+目标组列表）、BatchScanResponse（批次 ID+任务列表+统计）。
2. 新增 batch_scan_service：循环创建发现任务，异常隔离，记录批次事件。
3. 新增 route：POST /api/v1/scan/batch。
4. 在 main.py 注册 scan router。
5. 新增测试：正常批量创建、空 targets 校验、空 batches 校验。
6. 更新 README 批量扫描能力说明。
7. 运行定向测试与全量回归测试。

## 验收标准

- [ ] POST /api/v1/scan/batch 成功创建多个发现任务，返回 batch_id/tasks。
- [ ] 单组失败不影响其他组创建。
- [ ] 空 targets 或空 batches 返回 422。
- [ ] 定向测试与全量测试通过。
