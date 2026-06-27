from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.models.finding import Finding
from app.schemas.aggregation import (
    AssetAggregation,
    PluginFindingCount,
    ScanAggregationResponse,
    SeverityCount,
)


def _severity_breakdown(rows: list) -> SeverityCount:
    counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'unknown': 0}
    for row in rows:
        sev = (row[0] or 'unknown').lower()
        if sev in counts:
            counts[sev] += row[1]
        else:
            counts['unknown'] += row[1]
    return SeverityCount(**counts)


def query_scan_aggregation(tenant_id: str) -> ScanAggregationResponse:
    engine = get_engine()
    with Session(engine) as session:
        base = select(Finding).where(Finding.tenant_id == tenant_id)

        total_findings = session.execute(
            select(func.count()).select_from(base.subquery())
        ).scalar_one()

        sev_rows = session.execute(
            select(Finding.severity, func.count())
            .where(Finding.tenant_id == tenant_id)
            .group_by(Finding.severity)
        ).all()
        global_severity = _severity_breakdown(sev_rows)

        asset_rows = session.execute(
            select(Finding.asset_id)
            .where(Finding.tenant_id == tenant_id)
            .group_by(Finding.asset_id)
        ).all()
        asset_ids = [r[0] for r in asset_rows]

        total_assets = len(asset_ids)
        assets: list[AssetAggregation] = []

        for aid in asset_ids:
            sev_rows_a = session.execute(
                select(Finding.severity, func.count())
                .where(Finding.tenant_id == tenant_id, Finding.asset_id == aid)
                .group_by(Finding.severity)
            ).all()
            sev_a = _severity_breakdown(sev_rows_a)
            total_a = sum(v for v in sev_a.model_dump().values())

            plugin_rows = session.execute(
                select(Finding.plugin_id, func.count())
                .where(Finding.tenant_id == tenant_id, Finding.asset_id == aid)
                .group_by(Finding.plugin_id)
                .order_by(text('count(*) desc'))
            ).all()
            top_plugins = [PluginFindingCount(plugin_id=r[0], count=r[1]) for r in plugin_rows]

            assets.append(AssetAggregation(
                asset_id=aid,
                total_findings=total_a,
                severity_breakdown=sev_a,
                top_plugins=top_plugins,
            ))

    return ScanAggregationResponse(
        tenant_id=tenant_id,
        total_assets=total_assets,
        total_findings=total_findings,
        severity_breakdown=global_severity,
        assets=assets,
    )
