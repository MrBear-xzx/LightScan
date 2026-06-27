from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.main import app
from app.models.event import Event
from app.services.event_service import log_event_with_session


def test_job_retry_history_returns_paginated_items() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-a',
            payload={'new_job_id': 'new-a', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-b',
            payload={'new_job_id': 'new-b', 'job_type': 'ticket_sync', 'retry_count': 2},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries',
        params={'tenant_id': 't1', 'page': 1, 'page_size': 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['page'] == 1
    assert body['page_size'] == 1
    assert body['total'] >= 2
    assert len(body['items']) == 1
    item = body['items'][0]
    assert item['job_id'] in {'job-a', 'job-b'}
    assert item['new_job_id'] in {'new-a', 'new-b'}


def test_job_retry_history_supports_job_type_filter() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-notify',
            payload={'new_job_id': 'new-notify', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-ticket',
            payload={'new_job_id': 'new-ticket', 'job_type': 'ticket_sync', 'retry_count': 1},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries',
        params={'tenant_id': 't1', 'job_type': 'ticket_sync'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 1
    assert len(body['items']) == 1
    assert body['items'][0]['job_type'] == 'ticket_sync'
    assert body['items'][0]['job_id'] == 'job-ticket'


def test_job_retry_history_supports_time_window_filter() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-old',
            payload={'new_job_id': 'new-old', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-recent',
            payload={'new_job_id': 'new-recent', 'job_type': 'notification', 'retry_count': 2},
        )
        old_time = datetime.now(timezone.utc) - timedelta(days=2)
        recent_time = datetime.now(timezone.utc) - timedelta(hours=1)
        session.execute(
            update(Event).where(Event.reference_id == 'job-old').values(created_at=old_time),
        )
        session.execute(
            update(Event).where(Event.reference_id == 'job-recent').values(created_at=recent_time),
        )
        session.commit()

    from_time = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat().replace('+00:00', 'Z')
    to_time = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat().replace('+00:00', 'Z')

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries',
        params={
            'tenant_id': 't1',
            'requested_from': from_time,
            'requested_to': to_time,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 1
    assert len(body['items']) == 1
    assert body['items'][0]['job_id'] == 'job-recent'


def test_job_retry_history_rejects_invalid_time_window() -> None:
    client = TestClient(app)
    now = datetime.now(timezone.utc)
    response = client.get(
        '/api/v1/jobs/retries',
        params={
            'tenant_id': 't1',
            'requested_from': (now + timedelta(hours=1)).isoformat().replace('+00:00', 'Z'),
            'requested_to': now.isoformat().replace('+00:00', 'Z'),
        },
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'requested_from must be earlier than requested_to'


def test_job_retry_history_supports_source_job_id_keyword_filter() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='notify-prod-1001',
            payload={'new_job_id': 'new-notify-01', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='ticket-prod-1002',
            payload={'new_job_id': 'new-ticket-02', 'job_type': 'ticket_sync', 'retry_count': 1},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries',
        params={'tenant_id': 't1', 'job_id_keyword': 'notify-prod'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 1
    assert len(body['items']) == 1
    assert body['items'][0]['job_id'] == 'notify-prod-1001'


def test_job_retry_history_supports_new_job_id_keyword_filter() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-2001',
            payload={'new_job_id': 'notify-new-abc', 'job_type': 'notification', 'retry_count': 2},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-2002',
            payload={'new_job_id': 'ticket-new-def', 'job_type': 'ticket_sync', 'retry_count': 2},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries',
        params={'tenant_id': 't1', 'new_job_id_keyword': 'notify-new'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 1
    assert len(body['items']) == 1
    assert body['items'][0]['new_job_id'] == 'notify-new-abc'


def test_job_retry_history_supports_sort_order_asc() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-asc-old',
            payload={'new_job_id': 'new-asc-old', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-asc-new',
            payload={'new_job_id': 'new-asc-new', 'job_type': 'notification', 'retry_count': 2},
        )
        old_time = datetime.now(timezone.utc) - timedelta(days=1)
        new_time = datetime.now(timezone.utc)
        session.execute(
            update(Event).where(Event.reference_id == 'job-asc-old').values(created_at=old_time),
        )
        session.execute(
            update(Event).where(Event.reference_id == 'job-asc-new').values(created_at=new_time),
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries',
        params={'tenant_id': 't1', 'sort_order': 'asc'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['items'][0]['job_id'] == 'job-asc-old'


def test_job_retry_history_export_csv_supports_filters() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='notify-csv-1',
            payload={'new_job_id': 'notify-csv-new-1', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='ticket-csv-2',
            payload={'new_job_id': 'ticket-csv-new-2', 'job_type': 'ticket_sync', 'retry_count': 2},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries/export.csv',
        params={'tenant_id': 't1', 'job_type': 'notification'},
    )
    assert response.status_code == 200
    assert 'text/csv' in response.headers.get('content-type', '')
    assert 'job_id,new_job_id,job_type,retry_count,requested_at' in response.text
    assert 'notify-csv-1,notify-csv-new-1,notification,1,' in response.text
    assert 'ticket-csv-2' not in response.text


def test_job_retry_history_overview_returns_type_breakdown() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-ov-1',
            payload={'new_job_id': 'new-ov-1', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-ov-2',
            payload={'new_job_id': 'new-ov-2', 'job_type': 'notification', 'retry_count': 2},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-ov-3',
            payload={'new_job_id': 'new-ov-3', 'job_type': 'ticket_sync', 'retry_count': 1},
        )
        session.commit()

    client = TestClient(app)
    response = client.get('/api/v1/jobs/retries/overview', params={'tenant_id': 't1'})
    assert response.status_code == 200
    body = response.json()
    assert body['tenant_id'] == 't1'
    assert body['total_retries'] == 3
    assert body['job_type_counts']['notification'] == 2
    assert body['job_type_counts']['ticket_sync'] == 1
    assert body['retry_count_distribution']['1'] == 2
    assert body['retry_count_distribution']['2'] == 1
    assert body['unique_source_jobs'] == 3
    assert body['max_retry_count'] == 2
    assert body['avg_retry_count'] == 1.33
    assert body['latest_retry_count'] == 1
    assert body['latest_retry_job_type'] == 'ticket_sync'
    assert body['latest_source_job_id'] == 'job-ov-3'
    assert body['first_retry_requested_at'] is not None
    assert body['last_retry_requested_at'] is not None


def test_job_retry_history_overview_counts_unique_source_jobs() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-unique-1',
            payload={'new_job_id': 'new-unique-1a', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-unique-1',
            payload={'new_job_id': 'new-unique-1b', 'job_type': 'notification', 'retry_count': 2},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-unique-2',
            payload={'new_job_id': 'new-unique-2a', 'job_type': 'ticket_sync', 'retry_count': 1},
        )
        session.commit()

    client = TestClient(app)
    response = client.get('/api/v1/jobs/retries/overview', params={'tenant_id': 't1'})
    assert response.status_code == 200
    body = response.json()
    assert body['total_retries'] == 3
    assert body['unique_source_jobs'] == 2


def test_job_retry_history_overview_supports_job_type_filter() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-ov-filter-1',
            payload={'new_job_id': 'new-ov-filter-1', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-ov-filter-2',
            payload={'new_job_id': 'new-ov-filter-2', 'job_type': 'ticket_sync', 'retry_count': 3},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries/overview',
        params={'tenant_id': 't1', 'job_type': 'ticket_sync'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total_retries'] == 1
    assert body['job_type_counts']['ticket_sync'] == 1
    assert body['job_type_counts']['notification'] == 0
    assert body['retry_count_distribution']['3'] == 1
    assert body['unique_source_jobs'] == 1
    assert body['max_retry_count'] == 3
    assert body['avg_retry_count'] == 3.0
    assert body['latest_retry_count'] == 3
    assert body['latest_retry_job_type'] == 'ticket_sync'
    assert body['latest_source_job_id'] == 'job-ov-filter-2'
    assert body['first_retry_requested_at'] is not None
    assert body['last_retry_requested_at'] is not None


def test_job_retry_history_overview_supports_time_window_filter() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-ov-old',
            payload={'new_job_id': 'new-ov-old', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-ov-recent',
            payload={'new_job_id': 'new-ov-recent', 'job_type': 'ticket_sync', 'retry_count': 2},
        )
        old_time = datetime.now(timezone.utc) - timedelta(days=2)
        recent_time = datetime.now(timezone.utc) - timedelta(hours=1)
        session.execute(
            update(Event).where(Event.reference_id == 'job-ov-old').values(created_at=old_time),
        )
        session.execute(
            update(Event).where(Event.reference_id == 'job-ov-recent').values(created_at=recent_time),
        )
        session.commit()

    from_time = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat().replace('+00:00', 'Z')
    to_time = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat().replace('+00:00', 'Z')

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries/overview',
        params={
            'tenant_id': 't1',
            'requested_from': from_time,
            'requested_to': to_time,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total_retries'] == 1
    assert body['job_type_counts']['ticket_sync'] == 1
    assert body['job_type_counts']['notification'] == 0
    assert body['retry_count_distribution']['2'] == 1
    assert body['latest_source_job_id'] == 'job-ov-recent'


def test_job_retry_history_overview_rejects_invalid_time_window() -> None:
    client = TestClient(app)
    now = datetime.now(timezone.utc)
    response = client.get(
        '/api/v1/jobs/retries/overview',
        params={
            'tenant_id': 't1',
            'requested_from': (now + timedelta(hours=1)).isoformat().replace('+00:00', 'Z'),
            'requested_to': now.isoformat().replace('+00:00', 'Z'),
        },
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'requested_from must be earlier than requested_to'


def test_job_retry_history_export_csv_supports_columns_selection() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-col-1',
            payload={'new_job_id': 'new-col-1', 'job_type': 'notification', 'retry_count': 3},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries/export.csv',
        params={'tenant_id': 't1', 'columns': 'job_id,job_type,retry_count'},
    )
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert lines[0] == 'job_id,job_type,retry_count'
    assert lines[1].startswith('job-col-1,notification,3')


def test_job_retry_history_export_csv_rejects_unknown_columns() -> None:
    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries/export.csv',
        params={'tenant_id': 't1', 'columns': 'job_id,unknown_field'},
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'invalid columns parameter'


def test_job_retry_history_supports_columns_selection() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-list-col-1',
            payload={'new_job_id': 'new-list-col-1', 'job_type': 'notification', 'retry_count': 2},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries',
        params={'tenant_id': 't1', 'columns': 'job_id,job_type'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 1
    assert len(body['items']) == 1
    item = body['items'][0]
    assert set(item.keys()) == {'job_id', 'job_type'}
    assert item['job_id'] == 'job-list-col-1'
    assert item['job_type'] == 'notification'


def test_job_retry_history_rejects_unknown_columns() -> None:
    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries',
        params={'tenant_id': 't1', 'columns': 'job_id,unknown_field'},
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'invalid columns parameter'


def test_job_retry_history_supports_combined_filters() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='notify-combo-1',
            payload={'new_job_id': 'new-notify-match-1', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='notify-combo-2',
            payload={'new_job_id': 'new-notify-other-2', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='ticket-combo-3',
            payload={'new_job_id': 'new-ticket-match-3', 'job_type': 'ticket_sync', 'retry_count': 1},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries',
        params={
            'tenant_id': 't1',
            'job_type': 'notification',
            'job_id_keyword': 'notify-combo',
            'new_job_id_keyword': 'match',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 1
    assert len(body['items']) == 1
    assert body['items'][0]['job_id'] == 'notify-combo-1'


def test_job_retry_history_export_csv_supports_combined_filters() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='notify-csv-combo-1',
            payload={'new_job_id': 'new-notify-hit-1', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='ticket-csv-combo-2',
            payload={'new_job_id': 'new-ticket-hit-2', 'job_type': 'ticket_sync', 'retry_count': 1},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries/export.csv',
        params={
            'tenant_id': 't1',
            'job_type': 'notification',
            'job_id_keyword': 'notify-csv-combo',
            'new_job_id_keyword': 'hit-1',
        },
    )
    assert response.status_code == 200
    assert 'notify-csv-combo-1,new-notify-hit-1,notification,1,' in response.text
    assert 'ticket-csv-combo-2' not in response.text


def test_job_retry_history_overview_supports_source_job_id_keyword_filter() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='notify-ov-keyword-1',
            payload={'new_job_id': 'new-ov-keyword-a', 'job_type': 'notification', 'retry_count': 1},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='ticket-ov-keyword-2',
            payload={'new_job_id': 'new-ov-keyword-b', 'job_type': 'ticket_sync', 'retry_count': 2},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries/overview',
        params={'tenant_id': 't1', 'job_id_keyword': 'notify-ov-keyword'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total_retries'] == 1
    assert body['job_type_counts']['notification'] == 1
    assert body['job_type_counts']['ticket_sync'] == 0
    assert body['latest_source_job_id'] == 'notify-ov-keyword-1'


def test_job_retry_history_overview_supports_new_job_id_keyword_filter() -> None:
    engine = get_engine()
    with Session(engine) as session:
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-ov-new-keyword-1',
            payload={'new_job_id': 'notify-ov-new-keyword-hit', 'job_type': 'notification', 'retry_count': 2},
        )
        log_event_with_session(
            session,
            tenant_id='t1',
            event_type='job_retry_requested',
            reference_id='job-ov-new-keyword-2',
            payload={'new_job_id': 'ticket-ov-new-keyword-miss', 'job_type': 'ticket_sync', 'retry_count': 1},
        )
        session.commit()

    client = TestClient(app)
    response = client.get(
        '/api/v1/jobs/retries/overview',
        params={'tenant_id': 't1', 'new_job_id_keyword': 'notify-ov-new-keyword'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['total_retries'] == 1
    assert body['job_type_counts']['notification'] == 1
    assert body['job_type_counts']['ticket_sync'] == 0
    assert body['retry_count_distribution']['2'] == 1
