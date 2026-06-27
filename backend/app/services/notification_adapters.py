def build_feishu_payload(tenant_id: str, base: dict) -> dict:
    title = '[%s] ???? #%d' % (tenant_id, base['case_id'])
    text = '??: %s\\n????: %s\\n???: %s' % (
        base['state'], base['risk_score'], base.get('owner', 'unassigned'),
    )
    return {
        'msg_type': 'post',
        'content': {
            'post': {
                'zh_cn': {
                    'title': title,
                    'content': [[{'tag': 'text', 'text': text}]],
                }
            }
        },
    }


def build_dingtalk_payload(tenant_id: str, base: dict) -> dict:
    title = '???? #%d' % base['case_id']
    text = '## %s\\n- ??: %s\\n- ??: %s\\n- ????: %s\\n- ???: %s' % (
        title, tenant_id, base['state'], base['risk_score'], base.get('owner', 'unassigned'),
    )
    return {
        'msgtype': 'markdown',
        'markdown': {
            'title': title,
            'text': text,
        },
    }


def build_wecom_payload(tenant_id: str, base: dict) -> dict:
    content = '???? #%d\\n??: %s\\n??: %s\\n????: %s\\n???: %s' % (
        base['case_id'], tenant_id, base['state'], base['risk_score'], base.get('owner', 'unassigned'),
    )
    return {
        'msgtype': 'text',
        'text': {
            'content': content,
        },
    }


ADAPTER_BUILDERS = {
    'webhook': lambda t, b: dict(b, tenant_id=t),
    'feishu': build_feishu_payload,
    'dingtalk': build_dingtalk_payload,
    'wecom': build_wecom_payload,
}
