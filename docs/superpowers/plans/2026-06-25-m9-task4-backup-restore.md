# M9 任务4（备份与恢复）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供备份触发与备份列表查询接口，基于 events 表记录备份元数据。  
**Architecture:** 新增 /api/v1/ops/backups 端点，备份记录存储到 events 表（backup_created 事件）。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：BackupRecord、BackupListResponse、BackupCreateResponse。
2. 新增 backup_service：创建备份记录（占位）+ 列表查询。
3. 新增路由：GET/POST /api/v1/ops/backups。
4. 注册到 main.py。
5. 新增测试：空列表、创建+列表。
6. 更新 README。

## 验收标准

- [ ] GET /api/v1/ops/backups 返回备份记录列表。
- [ ] POST /api/v1/ops/backups 创建备份记录。
- [ ] 定向测试通过。
