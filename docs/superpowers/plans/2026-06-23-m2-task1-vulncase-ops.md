# M2 任务1（漏洞运营能力）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 M1 能力基础上，补齐漏洞运营最小闭环：Case 列表查询、负责人指派、SLA 设置、状态流转事件留痕。

**Architecture:** 保持现有 `route -> service -> model` 分层，在 API 路由只做参数校验与响应组装，把查询与更新逻辑下沉到 `vuln_case_service`。所有运营动作（指派、状态变更）统一写入 `events` 表，保证后续审计与报表可追溯。

**Tech Stack:** FastAPI、Pydantic v2、SQLAlchemy 2.x、PostgreSQL（Docker）、pytest

---

## 文件结构与职责

- 新建：`backend/app/services/vuln_case_service.py`
  - 负责 Case 查询、指派更新、SLA 更新、事件记录封装。
- 修改：`backend/app/schemas/vuln_case.py`
  - 增加列表查询参数、列表响应模型、指派请求/响应模型。
- 修改：`backend/app/api/routes/vuln_cases.py`
  - 新增 `GET /api/v1/vuln-cases`、`PATCH /api/v1/vuln-cases/{case_id}/assign`。
  - 补强现有状态流转接口的事件记录。
- 修改：`backend/app/services/event_service.py`
  - 增加对 `Session` 调用场景的兼容辅助函数（保持原接口不破坏）。
- 新建测试：`backend/tests/api/test_vuln_case_ops_api.py`
  - 覆盖列表过滤、排序、分页、指派、SLA 设置、事件写入。
- 修改测试：`backend/tests/api/_vuln_case_test_helper.py`
  - 增加批量造数与字段可配能力，支撑运营场景测试。

### 任务 1：补齐漏洞运营 API 契约测试（先红）

**Files:**
- Modify: `backend/tests/api/_vuln_case_test_helper.py`
- Create: `backend/tests/api/test_vuln_case_ops_api.py`

- [ ] **步骤 1：先写失败测试（列表/指派）**

```python
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.session import get_engine
from app.main import app
from tests.api._vuln_case_test_helper import seed_case


def test_vuln_case_list_supports_filters_and_sorting() -> None:
    engine = get_engine()
    now = datetime.now(timezone.utc)
    seed_case(engine, 201, state='confirmed', owner='alice', risk_score=8.8, sla_due_at=now + timedelta(days=1))
    seed_case(engine, 202, state='in_progress', owner='bob', risk_score=5.0, sla_due_at=now + timedelta(days=5))
    seed_case(engine, 203, state='confirmed', owner='alice', risk_score=9.3, sla_due_at=now - timedelta(days=1))

    client = TestClient(app)
    resp = client.get('/api/v1/vuln-cases', params={
        'tenant_id': 't1',
        'state': 'confirmed',
        'owner': 'alice',
        'overdue_only': True,
        'sort_by': 'risk_score',
        'sort_order': 'desc',
        'page': 1,
        'page_size': 20,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body['total'] == 1
    assert body['items'][0]['case_id'] == 203


def test_vuln_case_assign_updates_owner_and_sla_and_writes_event() -> None:
    engine = get_engine()
    seed_case(engine, 301, state='confirmed')

    client = TestClient(app)
    resp = client.patch('/api/v1/vuln-cases/301/assign', json={
        'owner': 'sec-oncall',
        'sla_due_at': '2026-07-01T00:00:00Z',
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body['case_id'] == 301
    assert body['owner'] == 'sec-oncall'
```

- [ ] **步骤 2：运行测试确认失败**

Run: `cd backend && python -m pytest tests/api/test_vuln_case_ops_api.py -q`
Expected: 因缺少列表/指派路由而 FAIL（404 或导入失败）。

- [ ] **步骤 3：提交（仅测试）**

```bash
git add backend/tests/api/_vuln_case_test_helper.py backend/tests/api/test_vuln_case_ops_api.py
git commit -m "test(vuln-case): 增加运营接口契约失败用例"
```

### 任务 2：实现 Case 列表查询（过滤/排序/分页）

**Files:**
- Create: `backend/app/services/vuln_case_service.py`
- Modify: `backend/app/schemas/vuln_case.py`
- Modify: `backend/app/api/routes/vuln_cases.py`

- [ ] **步骤 1：实现查询参数与响应模型**

```python
# backend/app/schemas/vuln_case.py
from datetime import datetime
from pydantic import BaseModel, Field


class VulnCaseListItem(BaseModel):
    case_id: int
    tenant_id: str
    asset_id: int
    risk_score: float
    state: str
    owner: str | None
    sla_due_at: datetime | None


class VulnCaseListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[VulnCaseListItem]
```

- [ ] **步骤 2：实现 service 查询逻辑**

```python
# backend/app/services/vuln_case_service.py
from datetime import datetime, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.vuln_case import VulnCase


def query_cases(
    session: Session,
    *,
    tenant_id: str,
    state: str | None,
    owner: str | None,
    overdue_only: bool,
    sort_by: str,
    sort_order: str,
    page: int,
    page_size: int,
) -> tuple[int, list[VulnCase]]:
    stmt: Select[tuple[VulnCase]] = select(VulnCase).where(VulnCase.tenant_id == tenant_id)
    if state:
        stmt = stmt.where(VulnCase.state == state)
    if owner:
        stmt = stmt.where(VulnCase.owner == owner)
    if overdue_only:
        stmt = stmt.where(VulnCase.sla_due_at.is_not(None), VulnCase.sla_due_at < datetime.now(timezone.utc))

    order_map = {
        'risk_score': VulnCase.risk_score,
        'sla_due_at': VulnCase.sla_due_at,
        'created_at': VulnCase.created_at,
    }
    order_col = order_map[sort_by]
    stmt = stmt.order_by(order_col.desc() if sort_order == 'desc' else order_col.asc())

    total = session.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    rows = session.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    return total, rows
```

- [ ] **步骤 3：实现列表路由**

```python
# backend/app/api/routes/vuln_cases.py
@router.get('', response_model=VulnCaseListResponse, summary='查询漏洞Case列表')
def list_vuln_cases(
    tenant_id: str,
    state: str | None = None,
    owner: str | None = None,
    overdue_only: bool = False,
    sort_by: str = 'risk_score',
    sort_order: str = 'desc',
    page: int = 1,
    page_size: int = 20,
) -> VulnCaseListResponse:
    ...
```

- [ ] **步骤 4：运行测试确认通过（列表场景）**

Run: `cd backend && python -m pytest tests/api/test_vuln_case_ops_api.py::test_vuln_case_list_supports_filters_and_sorting -q`
Expected: PASS（`1 passed`）。

- [ ] **步骤 5：提交**

```bash
git add backend/app/services/vuln_case_service.py backend/app/schemas/vuln_case.py backend/app/api/routes/vuln_cases.py
git commit -m "feat(vuln-case): 增加列表过滤排序分页能力"
```

### 任务 3：实现指派与 SLA 设置，并写入事件

**Files:**
- Modify: `backend/app/schemas/vuln_case.py`
- Modify: `backend/app/services/vuln_case_service.py`
- Modify: `backend/app/services/event_service.py`
- Modify: `backend/app/api/routes/vuln_cases.py`

- [ ] **步骤 1：扩展指派请求/响应模型**

```python
class VulnCaseAssignRequest(BaseModel):
    owner: str = Field(min_length=1, max_length=128)
    sla_due_at: datetime | None = None


class VulnCaseAssignResponse(BaseModel):
    case_id: int
    owner: str
    sla_due_at: datetime | None
```

- [ ] **步骤 2：实现 assign service（含事件）**

```python
# backend/app/services/vuln_case_service.py
def assign_case(session: Session, *, case_id: int, owner: str, sla_due_at: datetime | None) -> VulnCase:
    case = session.get(VulnCase, case_id)
    if case is None:
        raise ValueError('not_found')
    case.owner = owner
    case.sla_due_at = sla_due_at
    session.flush()
    log_event(
        session.connection(),
        tenant_id=case.tenant_id,
        event_type='vuln_case_assigned',
        reference_id=str(case.case_id),
        payload={'owner': owner, 'sla_due_at': sla_due_at.isoformat() if sla_due_at else None},
    )
    session.commit()
    session.refresh(case)
    return case
```

- [ ] **步骤 3：实现指派路由与异常映射**

```python
@router.patch('/{case_id}/assign', response_model=VulnCaseAssignResponse, summary='指派漏洞Case')
def assign_vuln_case(case_id: int, payload: VulnCaseAssignRequest) -> VulnCaseAssignResponse:
    ...
```

- [ ] **步骤 4：运行测试确认通过（指派场景）**

Run: `cd backend && python -m pytest tests/api/test_vuln_case_ops_api.py::test_vuln_case_assign_updates_owner_and_sla_and_writes_event -q`
Expected: PASS（`1 passed`）。

- [ ] **步骤 5：提交**

```bash
git add backend/app/schemas/vuln_case.py backend/app/services/vuln_case_service.py backend/app/services/event_service.py backend/app/api/routes/vuln_cases.py
git commit -m "feat(vuln-case): 增加负责人指派与SLA设置接口"
```

### 任务 4：补强状态流转事件留痕与回归测试

**Files:**
- Modify: `backend/app/api/routes/vuln_cases.py`
- Modify: `backend/tests/api/test_vuln_case_lifecycle.py`

- [ ] **步骤 1：为状态流转增加事件写入**

```python
log_event(
    session.connection(),
    tenant_id=case.tenant_id,
    event_type='vuln_case_state_changed',
    reference_id=str(case.case_id),
    payload={'from': current_state, 'to': payload.new_state},
)
```

- [ ] **步骤 2：增加回归测试（状态变更后事件存在）**

```python
def test_vuln_case_state_transition_writes_event() -> None:
    ...
```

- [ ] **步骤 3：运行相关测试**

Run: `cd backend && python -m pytest tests/api/test_vuln_case_lifecycle.py tests/api/test_vuln_case_ops_api.py -q`
Expected: PASS。

- [ ] **步骤 4：提交**

```bash
git add backend/app/api/routes/vuln_cases.py backend/tests/api/test_vuln_case_lifecycle.py backend/tests/api/test_vuln_case_ops_api.py
git commit -m "fix(vuln-case): 补齐状态流转事件审计与回归测试"
```

### 任务 5：全量验证与交付说明

**Files:**
- Modify: `README.md`

- [ ] **步骤 1：全量测试**

Run: `cd backend && python -m pytest tests -q`
Expected: 全部通过（当前基线应 >= 14 passed，新增后按实际数量）。

- [ ] **步骤 2：手工接口冒烟（可选但建议）**

Run:

```bash
# 启动依赖（若未运行）
docker compose -f deploy/docker-compose.yml up -d postgres --quiet-pull

# 仅示例，实际由 FastAPI 服务启动后调用
curl "http://127.0.0.1:8000/api/v1/vuln-cases?tenant_id=t1&sort_by=risk_score&sort_order=desc"
```

Expected: 返回 `total/page/page_size/items` 结构。

- [ ] **步骤 3：更新 README（仅补当前版本功能）**

```markdown
- 新增漏洞运营基础接口：Case 列表查询（过滤/排序/分页）、指派与 SLA 设置、状态流转事件审计。
```

- [ ] **步骤 4：提交**

```bash
git add README.md
git commit -m "docs(readme): 更新M2任务1可用能力说明"
```

## 最终验收清单

- [ ] `GET /api/v1/vuln-cases` 支持 `tenant_id/state/owner/overdue_only/sort/page`。
- [ ] `PATCH /api/v1/vuln-cases/{case_id}/assign` 可更新 `owner/sla_due_at`。
- [ ] `PATCH /api/v1/vuln-cases/{case_id}/state` 状态流转写入事件。
- [ ] API 测试、生命周期测试、全量测试均通过。
- [ ] README 已更新当前版本可展示能力。

## 规格覆盖自检

- 对齐 PRD 中“漏洞运营闭环（分派、流转、可追溯）”要求：已覆盖。
- 与现有插件/扫描链路耦合最小，不扩展无关范围：已控制。
- 未出现 TBD/TODO 占位项：已满足。
