from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.webhook_subscription import WebhookSubscription, WebhookSubscriptionListResponse, WebhookSubscriptionResponse
from app.services.webhook_subscription_service import create_subscription, delete_subscription, list_subscriptions

router = APIRouter(prefix='/api/v1/notifications/webhooks', tags=['notifications'])


@router.get('', response_model=WebhookSubscriptionListResponse)
def get_subs(tenant_id: str = Query(default='default')) -> WebhookSubscriptionListResponse:
    return list_subscriptions(tenant_id)


@router.post('', response_model=WebhookSubscriptionResponse, status_code=status.HTTP_201_CREATED)
def post_sub(payload: WebhookSubscription, tenant_id: str = Query(default='default')) -> WebhookSubscriptionResponse:
    return create_subscription(tenant_id, payload)


@router.delete('/{sub_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_sub(sub_id: int, tenant_id: str = Query(default='default')) -> None:
    deleted = delete_subscription(tenant_id, sub_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='subscription not found')
