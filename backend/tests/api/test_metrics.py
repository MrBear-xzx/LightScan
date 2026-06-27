from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.services.event_service import log_event_with_session


def test_metrics_endpoint_exposes_prometheus_style_text() -> None:
    client = TestClient(app)

    # 触发发现任务与通知派发，检查动态指标
    client.post(
        '/api/v1/discovery/tasks',
        json={'tenant_id': 't1', 'targets': ['example.com'], 'policy_id': 'default-external'},
    )
    client.post(
        '/api/v1/notifications/dispatch',
        json={'tenant_id': 't1', 'min_risk_score': 7.0},
    )

    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'lightscan_tasks_total' in response.text
    assert 'lightscan_discovery_tasks_total' in response.text
    assert 'lightscan_notification_dispatched_total' in response.text
    assert 'lightscan_notification_async_queued_total' in response.text
    assert 'lightscan_ticket_sync_async_queued_total' in response.text
    assert 'lightscan_notification_async_failed_total' in response.text
    assert 'lightscan_ticket_sync_async_failed_total' in response.text
    assert 'lightscan_job_retry_requested_total' in response.text
    assert 'lightscan_job_retry_failed_total' in response.text
    assert 'lightscan_job_retry_success_rate' in response.text
    assert 'lightscan_plugins_total' in response.text
    assert 'lightscan_plugins_healthy_total' in response.text
    assert 'lightscan_plugins_unhealthy_total' in response.text


def test_metrics_exposes_retry_quality_gauges() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='src-retry-1',
            payload={'new_job_id': 'retry-job-1', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='notification_async_failed',
            reference_id='retry-job-1',
            payload={'error': 'retry failed'},
        )
        session.commit()

    client = TestClient(app)
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'lightscan_job_retry_requested_total 1' in response.text
    assert 'lightscan_job_retry_failed_total 1' in response.text
    assert 'lightscan_job_retry_success_rate 0.0' in response.text


def test_metrics_exposes_plugin_health_counters() -> None:
    client = TestClient(app)
    response = client.get('/metrics')
    assert response.status_code == 200
    metrics_map: dict[str, float] = {}
    for line in response.text.splitlines():
        if not line or line.startswith('#') or ' ' not in line:
            continue
        key, value = line.split(' ', 1)
        metrics_map[key] = float(value)

    assert metrics_map['lightscan_plugins_total'] >= 2
    assert metrics_map['lightscan_plugins_healthy_total'] == metrics_map['lightscan_plugins_total']
    assert metrics_map['lightscan_plugins_unhealthy_total'] == 0
