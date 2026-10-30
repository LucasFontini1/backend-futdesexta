"""Entrega Web Push VAPID. Falhas não interrompem funcionalidades principais."""
import json
import os
from pywebpush import WebPushException, webpush
from core.models import PushSubscription


def send_push(user, title, link):
    private_key = os.getenv('VAPID_PRIVATE_KEY')
    subject = os.getenv('VAPID_SUBJECT')
    if not private_key or not subject:
        return False
    all_sent = True
    for subscription in PushSubscription.objects.filter(user=user):
        try:
            webpush(
                subscription_info={
                    'endpoint': subscription.endpoint,
                    'keys': {'p256dh': subscription.p256dh, 'auth': subscription.auth},
                },
                data=json.dumps({
                    'title': title, 'body': 'Você tem uma nova notificação.',
                    'url': link if link.startswith('/') and not link.startswith('//') else '/notificacoes',
                }),
                vapid_private_key=private_key,
                vapid_claims={'sub': subject},
                ttl=3600,
            )
        except WebPushException as exc:
            if exc.response is not None and exc.response.status_code in (404, 410):
                subscription.delete()
            else:
                all_sent = False
    return all_sent
