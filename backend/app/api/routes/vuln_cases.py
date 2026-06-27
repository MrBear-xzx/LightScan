from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.tenant_guard import require_tenant_guard
from app.db.session import get_engine
from app.models.asset import Asset
from app.models.vuln_case import VulnCase
from app.schemas.vuln_case import (
    _severity_from_risk,
    VulnCaseAssignRequest,
    VulnCaseAssignResponse,
    VulnCaseListItem,
    VulnCaseListResponse,
    VulnCaseStateResponse,
    VulnCaseStateUpdate,
)
from app.services.event_service import log_event
from app.services.lifecycle_service import validate_transition
from app.services.vuln_case_service import ORDER_BY_FIELDS, assign_case, query_cases

router = APIRouter(prefix='/api/v1/vuln-cases', tags=['vuln-cases'])


@router.get(
    '',
    response_model=VulnCaseListResponse,
    summary='查询漏洞Case列表',
    description='按租户维度查询漏洞Case，并支持过滤、排序与分页。',
    response_description='漏洞Case分页结果',
)
def list_vuln_cases(
    tenant_id: str = Depends(require_tenant_guard),
    state: str | None = None,
    owner: str | None = None,
    overdue_only: bool = False,
    sort_by: str = Query(default='risk_score', pattern='^(risk_score|sla_due_at|created_at)$'),
    sort_order: str = Query(default='desc', pattern='^(asc|desc)$'),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> VulnCaseListResponse:
    if sort_by not in ORDER_BY_FIELDS:
        raise HTTPException(status_code=400, detail='??????')

    engine = get_engine()
    with Session(engine) as session:
        total, rows = query_cases(
            session,
            tenant_id=tenant_id,
            state=state,
            owner=owner,
            overdue_only=overdue_only,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )
        _severity_map = _severity_from_risk
        _asset_cache: dict[int, str] = {}
        if rows:
            asset_ids = {r.asset_id for r in rows}
            asset_rows = session.execute(
                select(Asset).where(Asset.asset_id.in_(asset_ids))
            ).scalars().all()
            _asset_cache = {a.asset_id: a.canonical_identifier for a in asset_rows}

        items = [
            VulnCaseListItem(
                case_id=row.case_id,
                tenant_id=row.tenant_id,
                asset_id=row.asset_id,
                risk_score=row.risk_score,
                state=row.state,
                owner=row.owner,
                sla_due_at=row.sla_due_at,
                created_at=row.created_at,
                title=row.normalized_vuln_key,
                target=_asset_cache.get(row.asset_id, ""),
                severity=_severity_map(row.risk_score),
            )
            for row in rows
        ]
        return VulnCaseListResponse(total=total, page=page, page_size=page_size, items=items)


@router.patch(
    '/{case_id}/assign',
    response_model=VulnCaseAssignResponse,
    summary='指派漏洞Case',
    description='更新漏洞Case负责人与SLA到期时间。',
    response_description='指派结果',
)
def assign_vuln_case(
    case_id: int,
    payload: VulnCaseAssignRequest,
    tenant_id: str = Depends(require_tenant_guard),
) -> VulnCaseAssignResponse:
    engine = get_engine()
    with Session(engine) as session:
        try:
            case = assign_case(
                session,
                tenant_id=tenant_id,
                case_id=case_id,
                owner=payload.owner,
                sla_due_at=payload.sla_due_at,
            )
        except ValueError:
            raise HTTPException(status_code=404, detail='???????')

        return VulnCaseAssignResponse(
            case_id=case.case_id,
            owner=payload.owner,
            sla_due_at=payload.sla_due_at,
        )


@router.patch(
    '/{case_id}/state',
    response_model=VulnCaseStateResponse,
    summary='更新漏洞状态',
    description='更新指定漏洞 Case 的状态（当前为占位实现，用于联调与流程验证）。',
    response_description='状态更新结果',
)
def update_case_state(
    case_id: int,
    payload: VulnCaseStateUpdate,
    tenant_id: str = Depends(require_tenant_guard),
) -> VulnCaseStateResponse:
    engine = get_engine()
    with Session(engine) as session:
        stmt = select(VulnCase).where(
            VulnCase.case_id == case_id,
            VulnCase.tenant_id == tenant_id,
        )
        case = session.execute(stmt).scalar_one_or_none()
        if case is None:
            raise HTTPException(status_code=404, detail='???????')

        current_state = case.state
        if not validate_transition(current_state, payload.new_state):
            raise HTTPException(status_code=400, detail='??????')

        case.state = payload.new_state
        log_event(
            session.connection(),
            tenant_id=case.tenant_id,
            event_type='vuln_case_state_changed',
            reference_id=str(case.case_id),
            payload={'from': current_state, 'to': payload.new_state},
        )
        session.commit()
        return VulnCaseStateResponse(case_id=case.case_id, state=payload.new_state)
