from fastapi.testclient import TestClient

from app.main import app
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_engine
from app.models.vuln_case import VulnCase


def test_tag_crud() -> None:
    client = TestClient(app)

    # list empty
    resp = client.get('/api/v1/vuln-cases/tags', params={'tenant_id': 't1'})
    assert resp.status_code == 200
    assert resp.json()['total'] == 0

    # create
    create = client.post('/api/v1/vuln-cases/tags', json={
        'tenant_id': 't1', 'name': 'critical', 'color': '#ff0000',
    })
    assert create.status_code == 201
    tag_id = create.json()['tag_id']

    # list after create
    resp2 = client.get('/api/v1/vuln-cases/tags', params={'tenant_id': 't1'})
    assert resp2.json()['total'] == 1

    # delete
    delete = client.delete(f'/api/v1/vuln-cases/tags/{tag_id}', params={'tenant_id': 't1'})
    assert delete.status_code == 204

    # list after delete
    resp3 = client.get('/api/v1/vuln-cases/tags', params={'tenant_id': 't1'})
    assert resp3.json()['total'] == 0


def test_assign_tags_to_case() -> None:
    client = TestClient(app)
    # Ensure a case exists
    engine = get_engine()
    with Session(engine) as session:
        existing = session.execute(select(VulnCase).where(VulnCase.tenant_id == 't1').limit(1)).scalar_one_or_none()
        if not existing:
            case = VulnCase(tenant_id='t1', asset_id=1, normalized_vuln_key='assign-test', risk_score=5.0, state='new')
            session.add(case)
            session.commit()
            case_id = case.case_id
        else:
            case_id = existing.case_id

    tag = client.post('/api/v1/vuln-cases/tags', json={
        'tenant_id': 't1', 'name': 'p0',
    }).json()

    assign = client.post('/api/v1/vuln-cases/' + str(case_id) + '/tags', params={'tenant_id': 't1'}, json={
        'case_id': case_id, 'tag_ids': [tag['tag_id']],
    })
    assert assign.status_code == 200
    assert assign.json()['success']

    # query case tags
    case_tags = client.get('/api/v1/vuln-cases/' + str(case_id) + '/tags', params={'tenant_id': 't1'})
    assert case_tags.status_code == 200
    assert len(case_tags.json()) == 1
    assert case_tags.json()[0]['name'] == 'p0'


def test_assign_tags_rejects_unknown_case() -> None:
    client = TestClient(app)
    assign = client.post('/api/v1/vuln-cases/999999/tags', params={'tenant_id': 't1'}, json={
        'case_id': 999999, 'tag_ids': [],
    })
    assert assign.status_code == 404
