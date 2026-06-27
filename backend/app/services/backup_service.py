import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.event import Event
from app.schemas.backup import BackupCreateResponse, BackupListResponse, BackupRecord
from app.services.event_service import log_event_with_session


def list_backups(tenant_id: str) -> BackupListResponse:
    engine = get_engine()
    with Session(engine) as session:
        rows = session.execute(
            select(Event)
            .where(Event.tenant_id == tenant_id)
            .where(Event.event_type == 'backup_created')
            .order_by(Event.event_id.desc())
        ).scalars().all()

        items = []
        for row in rows:
            payload = json.loads(row.payload_json)
            items.append(BackupRecord(
                backup_id=row.reference_id,
                tenant_id=row.tenant_id,
                created_at=row.created_at.isoformat(),
                size_bytes=payload.get('size_bytes', 0),
                status=payload.get('status', 'completed'),
                description=payload.get('description', ''),
            ))

        return BackupListResponse(tenant_id=tenant_id, total=len(items), items=items)


def create_backup(tenant_id: str, description: str = '') -> BackupCreateResponse:
    backup_id = 'backup-' + uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id=tenant_id,
            event_type='backup_created',
            reference_id=backup_id,
            payload={
                'backup_id': backup_id,
                'status': 'completed',
                'size_bytes': 0,
                'description': description,
                'created_at': now.isoformat(),
            },
        )
        session.commit()

    return BackupCreateResponse(
        tenant_id=tenant_id,
        backup_id=backup_id,
        status='completed',
        message='backup record created (stub)',
    )
