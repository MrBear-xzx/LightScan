# M2 任务4（SLA 看板）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 SLA 看板接口，提供租户维度的 SLA 总览（总数、逾期、即将到期、无 SLA）与状态分布统计，支撑运营看板。

**Architecture:** 复用现有 reporting 分层结构：`route -> reporting_service -> schema`。路由仅处理参数与响应，统计逻辑集中在 service，确保后续扩展维度（owner、严重级别）时不侵入 API 层。

**Tech Stack:** FastAPI、SQLAlchemy、PostgreSQL、pytest

---

## 文件结构与职责

- 修改：`backend/app/schemas/reporting.py`
  - 新增 SLA 看板响应模型。
- 修改：`backend/app/services/reporting_service.py`
  - 新增 SLA 统计函数。
- 修改：`backend/app/api/routes/reports.py`
  - 新增 `GET /api/v1/reports/sla/overview`。
- 新增测试：`backend/tests/api/test_sla_dashboard_api.py`

## 任务 1：先写失败测试（RED）

**Files:**
- Create: `backend/tests/api/test_sla_dashboard_api.py`

- [ ] **步骤 1：新增 SLA 看板测试**

- 准备 t1 多条 case，覆盖：逾期、即将到期（<=48h）、正常、无 sla。
- 调用：`GET /api/v1/reports/sla/overview?tenant_id=t1`
- 断言：返回聚合字段正确，且不混入其他租户。

- [ ] **步骤 2：运行测试确认失败**

Run: `cd backend && python -m pytest tests/api/test_sla_dashboard_api.py -q`
Expected: 路由未实现导致 404 或断言失败。

## 任务 2：实现 SLA 统计 service（GREEN）

**Files:**
- Modify: `backend/app/services/reporting_service.py`

- [ ] **步骤 1：实现 `get_sla_overview`**

输出字段：
- `total_cases`
- `overdue_cases`（`sla_due_at < now` 且状态非 `fixed/ignored`）
- `due_48h_cases`（`now <= sla_due_at <= now+48h` 且状态非 `fixed/ignored`）
- `no_sla_cases`（`sla_due_at is null`）
- `status_counts`

## 任务 3：实现 schema 与 API 路由（GREEN）

**Files:**
- Modify: `backend/app/schemas/reporting.py`
- Modify: `backend/app/api/routes/reports.py`

- [ ] **步骤 1：新增 schema**

- `SlaOverviewStatusCounts`
- `SlaOverviewResponse`

- [ ] **步骤 2：新增路由**

- `GET /api/v1/reports/sla/overview?tenant_id=...`
- 返回 `SlaOverviewResponse`

## 任务 4：验证与文档同步

**Files:**
- Modify: `README.md`

- [ ] **步骤 1：运行定向测试**

Run: `cd backend && python -m pytest tests/api/test_sla_dashboard_api.py -q`
Expected: PASS。

- [ ] **步骤 2：运行全量测试**

Run: `cd backend && python -m pytest tests -q`
Expected: PASS。

- [ ] **步骤 3：更新 README 能力列表**

增加 SLA 看板接口说明。

## 最终验收清单

- [ ] `GET /api/v1/reports/sla/overview` 可返回 SLA 聚合结果。
- [ ] 统计不跨租户污染。
- [ ] API 测试与全量测试通过。

## 规格覆盖自检

- 对齐 M2 的“SLA 统计看板”目标。
- 不引入新依赖，不扩大到前端仪表盘，先确保后端指标可用。
- 无 TBD/TODO 占位项。
