# M3 任务17（任务重试历史关键字筛选）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强 `GET /api/v1/jobs/retries` 查询能力，支持按源任务ID与新任务ID关键字筛选重试记录。
**Architecture:** 在现有重试历史过滤链路上新增两个可选参数 `job_id_keyword/new_job_id_keyword`；查询流程维持“事件列表 -> payload 过滤 -> 分页返回”的模式，保持与既有 `job_type/时间窗口` 参数兼容。
**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 任务拆解

1. 新增失败测试：`job_id_keyword` 关键字筛选。
2. 新增失败测试：`new_job_id_keyword` 关键字筛选。
3. 扩展 retries 路由参数与过滤逻辑，支持双关键字过滤。
4. 运行定向测试与全量回归。
5. 更新 README 能力说明。

## 验收标准

- [ ] `GET /api/v1/jobs/retries` 支持 `job_id_keyword` 过滤。
- [ ] `GET /api/v1/jobs/retries` 支持 `new_job_id_keyword` 过滤。
- [ ] 与既有分页/类型/时间筛选可组合使用。
- [ ] 定向测试与全量测试通过。
