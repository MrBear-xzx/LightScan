from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.notification_template import (
    NotificationTemplate,
    NotificationTemplateListResponse,
    NotificationTemplateResponse,
)
from app.services.notification_template_service import (
    create_template,
    delete_template,
    get_template,
    list_templates,
)

router = APIRouter(prefix='/api/v1/notifications/templates', tags=['notifications'])


@router.get('', response_model=NotificationTemplateListResponse)
def get_templates(
    tenant_id: str = Query(default='default', min_length=1),
) -> NotificationTemplateListResponse:
    return list_templates(tenant_id)


@router.get('/{template_id}', response_model=NotificationTemplateResponse)
def get_template_by_id(
    template_id: int,
    tenant_id: str = Query(default='default', min_length=1),
) -> NotificationTemplateResponse:
    result = get_template(tenant_id, template_id)
    if result is None:
        raise HTTPException(status_code=404, detail='template not found')
    return result


@router.post('', response_model=NotificationTemplateResponse, status_code=status.HTTP_201_CREATED)
def post_template(payload: NotificationTemplate, tenant_id: str = Query(default='default', min_length=1)) -> NotificationTemplateResponse:
    return create_template(tenant_id, payload)


@router.delete('/{template_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_template(template_id: int, tenant_id: str = Query(default='default', min_length=1)) -> None:
    deleted = delete_template(tenant_id, template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='template not found')
