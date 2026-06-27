
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.vuln_tag import VulnTag
from app.models.vuln_case_tag import VulnCaseTag
from app.models.vuln_case import VulnCase
from app.schemas.vuln_tag import (
    VulnTagCreate,
    VulnTagListResponse,
    VulnTagResponse,
    VulnCaseTagAssignRequest,
)
from app.services.event_service import log_event_with_session


def list_tags(tenant_id: str) -> VulnTagListResponse:
    engine = get_engine()
    with Session(engine) as session:
        rows = session.execute(
            select(VulnTag).where(VulnTag.tenant_id == tenant_id).order_by(VulnTag.tag_id.desc())
        ).scalars().all()
        items = [_tag_to_response(r) for r in rows]
        return VulnTagListResponse(tenant_id=tenant_id, total=len(items), items=items)


def create_tag(req: VulnTagCreate) -> VulnTagResponse:
    engine = get_engine()
    with Session(engine) as session:
        row = VulnTag(tenant_id=req.tenant_id, name=req.name, color=req.color, description=req.description)
        session.add(row)
        session.commit()
        session.refresh(row)
    return _tag_to_response(row)


def delete_tag(tenant_id: str, tag_id: int) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(VulnTag).where(VulnTag.tenant_id == tenant_id, VulnTag.tag_id == tag_id)
        ).scalar_one_or_none()
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True


def assign_tags_to_case(tenant_id: str, req: VulnCaseTagAssignRequest) -> dict:
    engine = get_engine()
    with Session(engine) as session:
        case = session.execute(
            select(VulnCase).where(VulnCase.tenant_id == tenant_id, VulnCase.case_id == req.case_id)
        ).scalar_one_or_none()
        if case is None:
            return {'success': False, 'message': 'case not found'}

        # Remove existing tags for this case
        session.execute(
            select(VulnCaseTag).where(VulnCaseTag.case_id == req.case_id)
        ).scalars().all()
        # Delete all existing tags for this case
        existing = session.execute(
            select(VulnCaseTag).where(VulnCaseTag.case_id == req.case_id)
        ).scalars().all()
        for e in existing:
            session.delete(e)

        for tag_id in req.tag_ids:
            session.add(VulnCaseTag(case_id=req.case_id, tag_id=tag_id))

        log_event_with_session(
            session, tenant_id=tenant_id,
            event_type='vuln_case_tags_updated',
            reference_id=str(req.case_id),
            payload={'tag_ids': req.tag_ids},
        )
        session.commit()
        return {'success': True, 'case_id': req.case_id, 'tag_ids': req.tag_ids}


def get_tags_for_case(tenant_id: str, case_id: int) -> list[VulnTagResponse]:
    engine = get_engine()
    with Session(engine) as session:
        case = session.execute(
            select(VulnCase).where(VulnCase.tenant_id == tenant_id, VulnCase.case_id == case_id)
        ).scalar_one_or_none()
        if case is None:
            return []
        rows = session.execute(
            select(VulnTag)
            .join(VulnCaseTag, VulnTag.tag_id == VulnCaseTag.tag_id)
            .where(VulnCaseTag.case_id == case_id)
        ).scalars().all()
        return [_tag_to_response(r) for r in rows]


def _tag_to_response(row: VulnTag) -> VulnTagResponse:
    return VulnTagResponse(
        tag_id=row.tag_id,
        tenant_id=row.tenant_id,
        name=row.name,
        color=row.color,
        description=row.description,
    )
