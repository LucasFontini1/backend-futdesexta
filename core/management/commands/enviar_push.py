"""Envia alertas pendentes. Agendar fora da requisição, com credenciais VAPID."""

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Notification
from core.services.push import send_push


class Command(BaseCommand):
    help = 'Entrega notificações push ainda não enviadas.'

    def handle(self, *args, **options):
        sent = 0
        for notification in (
            Notification.objects.filter(push_sent_at__isnull=True).select_related('user').order_by('created_at')[:200]
        ):
            if send_push(notification.user, notification.title, notification.link):
                notification.push_sent_at = timezone.now()
                notification.save(update_fields=['push_sent_at'])
                sent += 1
        self.stdout.write(self.style.SUCCESS(f'Notificações processadas: {sent}'))
