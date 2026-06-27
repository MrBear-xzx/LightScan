import os
os.environ.setdefault('CELERY_TASK_ALWAYS_EAGER', '1')
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routes.discovery import router as discovery_router
from app.api.routes.health import router as health_router
from fastapi.responses import HTMLResponse
from app.api.routes.jobs import router as jobs_router
from app.api.routes.scan import router as scan_router
from app.api.routes.scan_detail import router as scan_detail_router
from app.api.routes.scan_policies import router as scan_policies_router
from app.api.routes.risk_rules import router as risk_rules_router
from app.api.routes.vuln_tags import router as vuln_tags_router
from app.api.routes.vuln_correlation import router as vuln_correlation_router
from app.api.routes.vuln_lifecycle import router as vuln_lifecycle_router
from app.api.routes.operation_logs import router as operation_logs_router
from app.api.routes.alert_rules import router as alert_rules_router
from app.api.routes.backups import router as backups_router
from app.api.routes.auth import router as auth_router
from app.api.routes.auth_rbac import router as auth_rbac_router
from app.middleware.audit_log import AuditLogMiddleware
from app.api.routes.projects import router as projects_router
from app.api.routes.notification_templates import router as notification_templates_router
from app.api.routes.webhook_subscriptions import router as webhook_subscriptions_router
from app.api.routes.scheduled_reports import router as scheduled_reports_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.plugins import router as plugins_router
from app.api.routes.reports import router as reports_router
from app.api.routes.tickets import router as tickets_router
from app.api.routes.vuln_cases import router as vuln_case_router
from app.db.session import ensure_tables

app = FastAPI(
    title='LightScan API',
    version='0.1.0',
    summary='漏洞分析平台最小可用 API',
    description=(
        'LightScan 当前版本提供 4 组基础能力：\n'
        '1. 健康检查\n'
        '2. 发现任务创建\n'
        '3. 漏洞状态流转（占位）\n'
        '4. 指标导出（Prometheus 格式）'
    ),
)
app.include_router(health_router)
app.include_router(discovery_router)
app.include_router(vuln_case_router)
app.include_router(metrics_router)
app.include_router(plugins_router)
app.include_router(reports_router)
app.include_router(notifications_router)
app.include_router(tickets_router)
app.include_router(jobs_router)
app.include_router(scan_router)
app.include_router(scan_detail_router)
app.include_router(scan_policies_router)
app.include_router(risk_rules_router)
app.include_router(vuln_tags_router)
app.include_router(vuln_correlation_router)
app.include_router(vuln_lifecycle_router)
app.include_router(operation_logs_router)
app.include_router(alert_rules_router)
app.include_router(backups_router)
app.include_router(auth_router)
app.include_router(auth_rbac_router)
app.include_router(scheduled_reports_router)
app.include_router(webhook_subscriptions_router)
app.include_router(notification_templates_router)
app.include_router(projects_router)
app.add_middleware(AuditLogMiddleware)




# Frontend SPA static files
STATIC_DIR = Path(__file__).parent / 'static'

if STATIC_DIR.exists() and any(STATIC_DIR.iterdir()):
    from fastapi import Request as _Req

    @app.middleware("http")
    async def _spa_middleware(request: _Req, call_next):
        response = await call_next(request)
        if response.status_code == 404:
            path = request.url.path
            if not path.startswith(('/api/', '/health/', '/metrics/', '/docs/', '/openapi/')):
                index = STATIC_DIR / 'index.html'
                if index.exists():
                    return HTMLResponse(content=index.read_text(encoding='utf-8'), status_code=200)
        return response

    app.mount('/', StaticFiles(directory=str(STATIC_DIR), html=True), name='static')

@app.on_event('startup')
def startup():
    ensure_tables()
