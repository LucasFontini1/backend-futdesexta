"""Publicação idempotente de notificações internas para membros autorizados."""
from core.models import Notification, TeamMembership


def notify_user(user, kind, title, link='', key=''):
    if key:
        notification, _ = Notification.objects.get_or_create(
            user=user, dedupe_key=key,
            defaults={'kind': kind, 'title': title, 'link': link},
        )
        return notification
    return Notification.objects.create(user=user, kind=kind, title=title, link=link)


def notify_team(team, kind, title, link='', key=''):
    members = TeamMembership.objects.filter(team=team).select_related('user')
    for membership in members:
        notify_user(
            membership.user, kind=kind, title=title,
            link=link, key=(f'{key}:{membership.user_id}' if key else ''),
        )
