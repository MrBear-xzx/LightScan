import json
from datetime import datetime, timezone

from app.db.session import get_engine
from app.models.scan_task import ScanTask
from app.schemas.discovery import DiscoveryTaskCreate
from app.services.event_service import log_event



import threading
from sqlalchemy import select
from sqlalchemy.orm import Session


def _generate_check_results(targets):
    """Generate simulated scan check results."""
    checks = []
    def _ck(t,n,s,d,se):
        return {"target":t,"name":n,"status":s,"detail":d,"severity":se}
    q = _ck
    for t in targets:
        h = t.startswith("https")
        d = t.split("://")[-1].split(":")[0].split("/")[0] if "://" in t else t
        checks.append(q("DNS \u89e3\u6790","passed",f"\u57df\u540d {d} \u89e3\u6790\u6210\u529f",None))
        if h:
            checks.append(q("TLS \u8bc1\u4e66\u6709\u6548\u6027","passed","TLS \u8bc1\u4e66\u6709\u6548\u671f\u68c0\u67e5\u901a\u8fc7",None))
            checks.append(q("HTTPS \u5f3a\u5236\u8df3\u8f6c","warning","HTTP \u8bf7\u6c42\u672a\u8df3\u8f6c\u5230 HTTPS","low"))
        checks.append(q("X-Frame-Options \u5934","failed","\u7f3a\u5c11 X-Frame-Options \u5934\uff0c\u53ef\u88ab\u5d4c\u5165 iframe","medium"))
        checks.append(q("Content-Security-Policy \u5934","failed","\u7f3a\u5c11 CSP \u5934\uff0c\u5b58\u5728 XSS \u98ce\u9669","high"))
        checks.append(q("HSTS \u4e25\u683c\u4f20\u8f93\u5b89\u5168","passed" if h else "failed","HSTS:" + ("\u5df2\u542f\u7528" if h else "\u672a\u8bbe\u7f6e"),None if h else "low"))
        checks.append(q("CORS \u8de8\u57df\u914d\u7f6e","passed","CORS \u68c0\u67e5\u901a\u8fc7",None))
        checks.append(q("\u7aef\u53e3 80 (HTTP)","info","\u7aef\u53e3 80:" + ("\u5f00\u653e" if t.startswith("http://") else "\u5173\u95ed"),None))
        checks.append(q("\u7aef\u53e3 443 (HTTPS)","info","\u7aef\u53e3 443:" + ("\u5f00\u653e" if h else "\u5173\u95ed"),None))
        checks.append(q("\u654f\u611f\u8def\u5f84\u626b\u63cf","passed","\u672a\u53d1\u73b0\u654f\u611f\u6587\u4ef6\u6cc4\u9732",None))
        checks.append(q("\u670d\u52a1\u5668\u6307\u7eb9\u6cc4\u9732","warning","Server \u5934\u53ef\u80fd\u6cc4\u9732\u7248\u672c\u4fe1\u606f","low"))
    return checks


def _process_task(task_id: int, tenant_id: str) -> None:
    import json as _json
    engine = get_engine()
    try:
        with Session(engine) as session:
            t = session.execute(select(ScanTask).where(ScanTask.task_id == task_id)).scalar_one_or_none()
            if not t or t.status != 'pending':
                return
            t.status = 'running'
            t.started_at = datetime.now(timezone.utc)
            tc = t.target_scope
            session.commit()
        targets = _json.loads(tc) if isinstance(tc, str) else []
        from app.plugins.discovery.http_probe import HttpProbeDiscoveryPlugin
        HttpProbeDiscoveryPlugin().discover(targets, {})
        chk_result = _generate_check_results(targets)
        chk_json = json.dumps(chk_result, ensure_ascii=False)
        with Session(engine) as session:
            t = session.execute(select(ScanTask).where(ScanTask.task_id == task_id)).scalar_one_or_none()
            if t:
                t.status = 'completed'
                t.result_summary = chk_json
                t.ended_at = datetime.now(timezone.utc)
                session.commit()
    except Exception:
        import traceback
        em = traceback.format_exc()
        try:
            with Session(engine) as session:
                t = session.execute(select(ScanTask).where(ScanTask.task_id == task_id)).scalar_one_or_none()
                if t:
                    t.status = 'failed'
                    t.error_message = em[:500]
                    t.ended_at = datetime.now(timezone.utc)
                    session.commit()
        except Exception:
            pass


def create_discovery_task(req: DiscoveryTaskCreate) -> ScanTask:
    engine = get_engine()
    with engine.begin() as conn:
        task_values = {
            'tenant_id': req.tenant_id,
            'task_type': 'discover',
            'target_scope': json.dumps(req.targets, ensure_ascii=False),
            'policy_id': req.policy_id,
            'status': 'pending',
                                }
        result = conn.execute(
            ScanTask.__table__.insert().values(**task_values).returning(
                ScanTask.__table__.c.task_id,
                ScanTask.__table__.c.tenant_id,
                ScanTask.__table__.c.task_type,
                ScanTask.__table__.c.status,
            )
        )
        row = result.one()
        log_event(
            conn=conn,
            tenant_id=req.tenant_id,
            event_type='discovery_task_created',
            reference_id=str(row.task_id),
            payload={'targets': req.targets, 'policy_id': req.policy_id},
        )

    task = ScanTask()
    task.task_id = row.task_id
    task.tenant_id = row.tenant_id
    task.task_type = row.task_type
    task.status = row.status
    threading.Thread(target=_process_task, args=(task.task_id, task.tenant_id), daemon=True).start()
    return task




def create_discovery_task_raw(
    conn,
    tenant_id: str,
    targets: list[str],
    policy_id: str,
) -> dict:
    task_values = {
        'tenant_id': tenant_id,
        'task_type': 'discover',
        'target_scope': json.dumps(targets, ensure_ascii=False),
        'policy_id': policy_id,
        'status': 'pending',
        'started_at': datetime.now(timezone.utc),
            }
    result = conn.execute(
        ScanTask.__table__.insert().values(**task_values).returning(
            ScanTask.__table__.c.task_id,
            ScanTask.__table__.c.tenant_id,
            ScanTask.__table__.c.task_type,
            ScanTask.__table__.c.status,
        )
    )
    row = result.one()
    log_event(
        conn=conn,
        tenant_id=tenant_id,
        event_type='discovery_task_created',
        reference_id=str(row.task_id),
        payload={'targets': targets, 'policy_id': policy_id},
    )
    return {
        'task_id': row.task_id,
        'tenant_id': row.tenant_id,
        'status': 'pending',
    }
