# M3 任务20（任务重试历史 CSV 导出）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增加重试历史 CSV 导出能力，支持运营与审计侧离线分析。
**Architecture:** 新增 `GET /api/v1/jobs/retries/export.csv`，复用重试历史筛选参数（类型、关键字、时间窗口、排序方向）导出 CSV；数据来源保持 `job_retry_requested` 事件，不新增表结构。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：CSV 导出接口可用并支持 `job_type` 过滤。
2. 新增路由实现：查询事件并输出 CSV（含响应头）。
3. 保持筛选参数一致性：`sort_order/job_type/job_id_keyword/new_job_id_keyword/requested_from/requested_to`。
4. 运行定向测试与全量回归。
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries/export.csv` 返回可下载 CSV。
- [ ] 导出接口支持与列表接口一致的筛选参数。
- [ ] CSV 包含字段：`job_id,new_job_id,job_type,retry_count,requested_at`。
- [ ] 定向测试与全量测试通过。
