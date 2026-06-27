# M2 任务3（报表导出与通知留痕）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有报表汇总与通知预览基础上，补齐“可导出（CSV）+ 可审计（通知事件落库）”能力，形成最小运营闭环。

**Architecture:** 继续保持 route -> service -> model 分层。CSV 内容由报表 service 统一生成，路由仅负责请求参数与响应媒体类型；通知发送阶段暂不接入外部通道，仅通过 preview + event log 模拟“待发送通知”写入，保证后续对接 IM/邮件时不改动主流程。

**Tech Stack:** FastAPI、SQLAlchemy、PostgreSQL、pytest

---

## 文件结构与职责

- 修改：`backend/app/api/routes/reports.py`
  - 新增 `GET /api/v1/reports/vuln/export.csv`。
- 修改：`backend/app/services/reporting_service.py`
  - 新增 CSV 生成函数（含表头、过滤与排序最小能力）。
- 修改：`backend/app/api/routes/notifications.py`
  - 新增 `POST /api/v1/notifications/dispatch`（模拟派发并写事件）。
- 修改：`backend/app/services/notification_service.py`
  - 新增 dispatch 逻辑：筛选候选 case + 写 `events`。
- 修改：`backend/app/schemas/notification.py`
  - 增加 dispatch 请求与响应模型。
- 新增测试：`backend/tests/api/test_reporting_export_and_dispatch_api.py`

## 任务 1：先写失败测试（RED）

**Files:**
- Create: `backend/tests/api/test_reporting_export_and_dispatch_api.py`

- [ ] **步骤 1：新增 CSV 导出失败测试**

```python
def test_vuln_report_export_csv() -> None:
    ...
    r = client.get('/api/v1/reports/vuln/export.csv', params={'tenant_id': 't1'})
    assert r.status_code == 200
    assert 'text/csv' in r.headers['content-type']
    assert 'case_id,tenant_id,state,risk_score,owner' in r.text
```

- [ ] **步骤 2：新增通知派发失败测试**

```python
def test_notification_dispatch_writes_events() -> None:
    ...
    r = client.post('/api/v1/notifications/dispatch', json={'tenant_id': 't1', 'min_risk_score': 7.0})
    assert r.status_code == 200
    assert r.json()['dispatched'] >= 1
```

- [ ] **步骤 3：运行测试确认失败**

Run: `cd backend && python -m pytest tests/api/test_reporting_export_and_dispatch_api.py -q`
Expected: 因路由缺失返回 404 或断言失败。

## 任务 2：实现报表 CSV 导出（GREEN）

**Files:**
- Modify: `backend/app/services/reporting_service.py`
- Modify: `backend/app/api/routes/reports.py`

- [ ] **步骤 1：实现 service 查询与 CSV 构建**

- 查询当前租户 `vuln_cases`，按 `risk_score desc` 排序，导出字段：`case_id,tenant_id,state,risk_score,owner`。
- 使用标准库 `csv` + `io.StringIO` 输出。

- [ ] **步骤 2：实现 CSV 路由**

- `GET /api/v1/reports/vuln/export.csv?tenant_id=...`
- `media_type='text/csv; charset=utf-8'`
- 增加 `Content-Disposition` 文件名。

- [ ] **步骤 3：运行目标测试**

Run: `cd backend && python -m pytest tests/api/test_reporting_export_and_dispatch_api.py::test_vuln_report_export_csv -q`
Expected: PASS。

## 任务 3：实现通知派发与事件留痕（GREEN）

**Files:**
- Modify: `backend/app/schemas/notification.py`
- Modify: `backend/app/services/notification_service.py`
- Modify: `backend/app/api/routes/notifications.py`

- [ ] **步骤 1：新增 dispatch schema**

- `NotificationDispatchRequest(tenant_id, min_risk_score)`
- `NotificationDispatchResponse(tenant_id, min_risk_score, dispatched)`

- [ ] **步骤 2：实现 dispatch service**

- 复用 preview 过滤逻辑获取候选 case。
- 对每个候选写 `events`：`event_type='notification_dispatched'`。
- 返回派发数量。

- [ ] **步骤 3：实现 dispatch 路由**

- `POST /api/v1/notifications/dispatch`
- 调 service 并返回响应。

- [ ] **步骤 4：运行目标测试**

Run: `cd backend && python -m pytest tests/api/test_reporting_export_and_dispatch_api.py::test_notification_dispatch_writes_events -q`
Expected: PASS。

## 任务 4：回归与交付

**Files:**
- Modify: `README.md`（更新当前测试通过数与新接口能力）

- [ ] **步骤 1：运行相关测试**

Run: `cd backend && python -m pytest tests/api/test_reporting_and_notification_api.py tests/api/test_reporting_export_and_dispatch_api.py -q`
Expected: PASS。

- [ ] **步骤 2：运行全量测试**

Run: `cd backend && python -m pytest tests -q`
Expected: PASS。

- [ ] **步骤 3：提交**

```bash
git add backend/app/api/routes/reports.py backend/app/api/routes/notifications.py backend/app/services/reporting_service.py backend/app/services/notification_service.py backend/app/schemas/notification.py backend/tests/api/test_reporting_export_and_dispatch_api.py README.md
git commit -m "feat(reporting): 增加CSV导出与通知派发事件留痕"
```

## 最终验收清单

- [ ] `GET /api/v1/reports/vuln/export.csv` 可下载 CSV。
- [ ] `POST /api/v1/notifications/dispatch` 返回派发数量。
- [ ] `events` 存在 `notification_dispatched` 记录。
- [ ] API 相关测试 + 全量测试通过。

## 规格覆盖自检

- 覆盖“报表导出”与“通知闭环最小可审计”两个 M2 关键点。
- 不引入外部依赖安装，不扩大范围到真实第三方通知。
- 无 TBD/TODO 占位项。
