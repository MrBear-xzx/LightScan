from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_smoke_pipeline_definition_exists() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    compose_file = repo_root / 'deploy' / 'docker-compose.yml'
    content = compose_file.read_text(encoding='utf-8')
    assert 'postgres' in content
    assert 'redis' in content
    assert 'backend' in content


def test_release_rollback_template_exists() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    release_template = repo_root / 'docs' / 'operations' / 'release-rollback-template.md'
    content = release_template.read_text(encoding='utf-8')
    assert '发布前检查清单' in content
    assert '回滚步骤' in content


def test_min_e2e_smoke_pipeline_endpoints() -> None:
    client = TestClient(app)

    health = client.get('/health')
    assert health.status_code == 200
    assert health.json() == {'status': 'ok'}

    discovery = client.post(
        '/api/v1/discovery/tasks',
        json={'tenant_id': 't1', 'targets': ['example.com'], 'policy_id': 'default-external'},
    )
    assert discovery.status_code == 201

    notify_async = client.post(
        '/api/v1/notifications/dispatch',
        json={
            'tenant_id': 't1',
            'provider': 'webhook',
            'min_risk_score': 7.0,
            'mode': 'async',
        },
    )
    assert notify_async.status_code == 200
    notify_job_id = notify_async.json().get('job_id')
    assert notify_job_id

    ticket_async = client.post(
        '/api/v1/tickets/sync',
        json={
            'tenant_id': 't1',
            'provider': 'mock_jira',
            'case_ids': [1],
            'mode': 'async',
        },
    )
    assert ticket_async.status_code == 200
    ticket_job_id = ticket_async.json().get('job_id')
    assert ticket_job_id

    job_status = client.get(
        '/api/v1/jobs/status',
        params={'tenant_id': 't1', 'job_id': notify_job_id},
    )
    assert job_status.status_code == 200
    assert job_status.json()['status'] in {'queued', 'success', 'failed'}

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    assert 'lightscan_notification_async_queued_total' in metrics.text
    assert 'lightscan_ticket_sync_async_queued_total' in metrics.text
