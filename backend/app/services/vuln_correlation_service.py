from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.vuln_case import VulnCase
from app.schemas.vuln_correlation import (
    AssetCorrelationItem,
    VulnCaseSummary,
    VulnCorrelationResponse,
)


def query_vuln_correlation(tenant_id: str) -> VulnCorrelationResponse:
    engine = get_engine()
    with Session(engine) as session:
        # Get all distinct asset_ids for this tenant
        asset_rows = session.execute(
            select(VulnCase.asset_id)
            .where(VulnCase.tenant_id == tenant_id)
            .group_by(VulnCase.asset_id)
        ).all()
        asset_ids = [r[0] for r in asset_rows]
        total_cases_query = session.execute(
            select(func.count()).select_from(
                select(VulnCase).where(VulnCase.tenant_id == tenant_id).subquery()
            )
        )
        total_cases = total_cases_query.scalar_one()

        items: list[AssetCorrelationItem] = []
        for aid in asset_ids:
            base = select(VulnCase).where(VulnCase.tenant_id == tenant_id, VulnCase.asset_id == aid)
            total = session.execute(
                select(func.count()).select_from(base.subquery())
            ).scalar_one()

            # Count by risk score thresholds
            all_rows = session.execute(
                base.order_by(VulnCase.risk_score.desc())
            ).scalars().all()

            critical = sum(1 for r in all_rows if r.risk_score >= 8.0)
            high = sum(1 for r in all_rows if 6.0 <= r.risk_score < 8.0)
            medium = sum(1 for r in all_rows if 3.0 <= r.risk_score < 6.0)
            low = sum(1 for r in all_rows if r.risk_score < 3.0)

            top = all_rows[0] if all_rows else None
            top_risk = None
            if top:
                top_risk = VulnCaseSummary(
                    case_id=top.case_id,
                    risk_score=top.risk_score,
                    state=top.state,
                    owner=top.owner,
                    created_at=top.created_at.isoformat(),
                )

            items.append(AssetCorrelationItem(
                asset_id=aid,
                total_cases=total,
                critical_count=critical,
                high_count=high,
                medium_count=medium,
                low_count=low,
                top_risk_case=top_risk,
            ))

        return VulnCorrelationResponse(
            tenant_id=tenant_id,
            total_assets=len(asset_ids),
            total_cases=total_cases,
            items=items,
        )
