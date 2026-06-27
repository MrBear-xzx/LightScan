from app.services.notification_adapters import (
    build_dingtalk_payload,
    build_feishu_payload,
    build_wecom_payload,
)


def test_feishu_payload() -> None:
    base = {'case_id': 1, 'risk_score': 7.5, 'state': 'new', 'owner': 'admin'}
    payload = build_feishu_payload('t1', base)
    assert payload['msg_type'] == 'post'
    assert '????' in payload['content']['post']['zh_cn']['title']


def test_dingtalk_payload() -> None:
    base = {'case_id': 2, 'risk_score': 8.0, 'state': 'confirmed', 'owner': 'analyst'}
    payload = build_dingtalk_payload('t1', base)
    assert payload['msgtype'] == 'markdown'
    assert '????' in payload['markdown']['title']


def test_wecom_payload() -> None:
    base = {'case_id': 3, 'risk_score': 5.0, 'state': 'new', 'owner': None}
    payload = build_wecom_payload('t1', base)
    assert payload['msgtype'] == 'text'
    assert '????' in payload['text']['content']
