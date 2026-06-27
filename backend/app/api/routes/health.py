from fastapi import APIRouter

router = APIRouter(tags=['system'])


@router.get(
    '/health',
    summary='健康检查',
    description='用于检查服务是否可用。返回 status=ok 表示 API 进程正常。',
    response_description='健康状态结果',
)
def health() -> dict[str, str]:
    return {'status': 'ok'}
