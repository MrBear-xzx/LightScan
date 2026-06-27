# M2 任务5（SLA 趋势接口）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 SLA 趋势接口，按天输出近 N 天（默认 7 天）的逾期数量与总数量变化，支撑趋势看板与预警。

**Architecture:** 继续复用 reporting 分层，趋势计算在 `reporting_service`，API 路由只负责参数解析与响应组装。先按 `created_at` 所在日期聚合，保证可用性，再迭代更细粒度口径。

**Tech Stack:** FastAPI、SQLAlchemy、PostgreSQL、pytest

---

## 文件结构与职责

- 修改：`backend/app/schemas/reporting.py`
  - 新增 SLA 趋势响应模型。
- 修改：`backend/app/services/reporting_service.py`
  - 新增趋势统计函数。
- 修改：`backend/app/api/routes/reports.py`
  - 新增 `GET /api/v1/reports/sla/trend`。
- 新增测试：`backend/tests/api/test_sla_trend_api.py`

## 任务 1：先写失败测试（RED）

- [ ] 新增趋势接口测试，断言返回字段：`tenant_id/days/points`。
- [ ] 使用 `seed_case` 造多条数据并校验 points 长度与字段完整性。
- [ ] 运行：`cd backend && python -m pytest tests/api/test_sla_trend_api.py -q`，预期失败（404）。

## 任务 2：实现 schema + service + route（GREEN）

- [ ] 在 `reporting.py` 新增：
  - `SlaTrendPoint`（date/overdue_cases/total_cases）
  - `SlaTrendResponse`（tenant_id/days/points）
- [ ] 在 `reporting_service.py` 新增 `get_sla_trend(session, tenant_id, days)`：
  - 生成最近 N 天日期序列
  - 统计每日日新增 case 总数（按 created_at 日期）
  - 统计其中逾期 case 数（`sla_due_at < now` 且状态非 `fixed/ignored`）
- [ ] 在 `reports.py` 新增：
  - `GET /api/v1/reports/sla/trend?tenant_id=...&days=7`
  - `days` 限制 `1~30`

## 任务 3：验证与文档同步

- [ ] 运行：`cd backend && python -m pytest tests/api/test_sla_trend_api.py -q`（PASS）
- [ ] 运行：`cd backend && python -m pytest tests -q`（PASS）
- [ ] 更新 `README.md` 增加 SLA 趋势接口说明

## 最终验收清单

- [ ] `GET /api/v1/reports/sla/trend` 可返回趋势序列
- [ ] 支持 `days` 参数，返回长度正确
- [ ] 全量测试通过

## 规格覆盖自检

- 覆盖 M2 的 SLA 趋势能力缺口。
- 不引入新依赖，不扩大到前端图表组件。
- 无 TBD/TODO 占位项。
