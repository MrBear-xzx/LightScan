# M8 任务4（定时报表推送）实施计划
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 提供定时报表推送配置管理，支持按 Cron 表达式定时推送报表到指定渠道。  
**Architecture:** 基于 policy 表（scheduled_report_ 前缀）持久化，提供 CRUD 接口。（实际调度需集成 Celery/Cron 任务）。  
**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、pytest

## 任务拆解

1. 新增 schema：ScheduledReportConfig、ScheduledReportResponse、ScheduledReportListResponse。
2. 新增 scheduled_report_service：基于 policy 表 CRUD。
3. 新增路由：GET/POST/DELETE /api/v1/reports/scheduled。
4. 注册到 main.py。
5. 新增测试：CRUD 全流程。
6. 更新 README。

## 验收标准

- [ ] 定时报表支持名称、类型、Cron、渠道、Webhook URL 等配置。
- [ ] CRUD 接口完整可用。
- [ ] 定向测试通过。
