from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.asset import Asset


def test_asset_unique_constraint_enforced(db_engine) -> None:
    with Session(db_engine) as session:
        first = Asset(
            tenant_id='t1',
            asset_type='domain',
            canonical_identifier='example.com',
            criticality=3,
            status='active',
        )
        second = Asset(
            tenant_id='t1',
            asset_type='domain',
            canonical_identifier='example.com',
            criticality=2,
            status='active',
        )
        session.add(first)
        session.commit()
        session.add(second)
        raised = False
        try:
            session.commit()
        except IntegrityError:
            raised = True
        assert raised is True
