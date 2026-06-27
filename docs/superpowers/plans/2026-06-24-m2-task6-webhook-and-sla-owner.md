# M2 任务6（Webhook 通知 + SLA Owner 维度）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有通知与 SLA 看板基础上，新增 webhook 真实发送能力（可配置）并补齐 SLA 看板 owner 维度聚合。

**Architecture:** 保持 route -> service -> schema。通知发送增加 provider 抽象（先实现 webhook provider）；SLA 看板 owner 聚合在 reporting service 内统一计算，避免在路由层拼装统计。

**Tech Stack:** FastAPI、SQLAlchemy、pytest

---

## 文件结构与职责

- 修改：`backend/app/schemas/notification.py`
  - 增加 webhook 配置与派发结果字段（成功/失败）。
- 修改：`backend/app/services/notification_service.py`
  - 增加 webhook 发送函数与 dispatch 执行结果。
- 修改：`backend/app/api/routes/notifications.py`
  - dispatch 接口支持 webhook URL。
- 修改：`backend/app/schemas/reporting.py`
  - 增加 owner 维度结构。
- 修改：`backend/app/services/reporting_service.py`
  - 在 `get_sla_overview` 返回 owner 维度聚合。
- 新增测试：`backend/tests/api/test_notification_webhook_and_sla_owner_api.py`

## 任务 1：先写失败测试（RED）

- [ ] 新增 webhook 派发测试：传入 `webhook_url`，断言返回 `sent/failed` 字段。
- [ ] 新增 SLA owner 聚合测试：断言 `owner_breakdown` 包含 owner 维度统计。
- [ ] 运行：`cd backend && python -m pytest tests/api/test_notification_webhook_and_sla_owner_api.py -q`
- [ ] 预期：失败（字段或逻辑未实现）。

## 任务 2：实现 webhook 派发最小能力（GREEN）

- [ ] 扩展 dispatch request/response schema：
  - request: `webhook_url: str | None`
  - response: `dispatched/sent/failed`
- [ ] service 增加 webhook 发送（使用 `urllib.request`，避免新增依赖）：
  - 成功：记录 `notification_webhook_sent`
  - 失败：记录 `notification_webhook_failed`
- [ ] 若未传 `webhook_url`，保持模拟模式（兼容现有行为）。

## 任务 3：实现 SLA owner 维度聚合（GREEN）

- [ ] `get_sla_overview` 增加 `owner_breakdown`，每个 owner 输出：
  - `total_cases`
  - `overdue_cases`
- [ ] owner 为空统一为 `unassigned`。

## 任务 4：验证与文档同步

- [ ] 定向测试：`cd backend && python -m pytest tests/api/test_notification_webhook_and_sla_owner_api.py -q`
- [ ] 全量测试：`cd backend && python -m pytest tests -q`
- [ ] 更新 README 新增 webhook 与 owner 维度说明。

## 最终验收清单

- [ ] dispatch 支持 webhook URL 并返回 sent/failed。
- [ ] SLA overview 返回 owner_breakdown。
- [ ] 全量测试通过。

## 规格覆盖自检

- 覆盖“真实通知通道最小接入 + SLA owner 维度”目标。
- 不新增外部依赖安装，不超出后端能力边界。
- 无 TBD/TODO 占位项。
