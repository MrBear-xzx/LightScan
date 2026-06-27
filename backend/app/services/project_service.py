from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.project import Project, ProjectMember
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectMemberAdd,
    ProjectMemberResponse,
    ProjectResponse,
)
from app.services.event_service import log_event_with_session


def list_projects(tenant_id: str) -> ProjectListResponse:
    engine = get_engine()
    with Session(engine) as session:
        rows = session.execute(
            select(Project).where(Project.tenant_id == tenant_id).order_by(Project.project_id.desc())
        ).scalars().all()
        items = [ProjectResponse(project_id=r.project_id, tenant_id=r.tenant_id, name=r.name, description=r.description) for r in rows]
        return ProjectListResponse(tenant_id=tenant_id, total=len(items), items=items)


def create_project(req: ProjectCreate) -> ProjectResponse:
    engine = get_engine()
    with Session(engine) as session:
        row = Project(tenant_id=req.tenant_id, name=req.name, description=req.description)
        session.add(row)
        session.commit()
        session.refresh(row)
        log_event_with_session(session, tenant_id=req.tenant_id, event_type='project_created', reference_id=str(row.project_id), payload={'name': req.name})
    return ProjectResponse(project_id=row.project_id, tenant_id=row.tenant_id, name=row.name, description=row.description)


def delete_project(tenant_id: str, project_id: int) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        row = session.execute(
            select(Project).where(Project.tenant_id == tenant_id, Project.project_id == project_id)
        ).scalar_one_or_none()
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True


def add_member(tenant_id: str, project_id: int, req: ProjectMemberAdd) -> ProjectMemberResponse:
    engine = get_engine()
    with Session(engine) as session:
        row = ProjectMember(project_id=project_id, user_id=req.user_id, role=req.role)
        session.add(row)
        session.commit()
        session.refresh(row)
    return ProjectMemberResponse(id=row.id, project_id=row.project_id, user_id=row.user_id, role=row.role)


def list_members(tenant_id: str, project_id: int) -> list[ProjectMemberResponse]:
    engine = get_engine()
    with Session(engine) as session:
        rows = session.execute(
            select(ProjectMember).where(ProjectMember.project_id == project_id)
        ).scalars().all()
    return [ProjectMemberResponse(id=r.id, project_id=r.project_id, user_id=r.user_id, role=r.role) for r in rows]
