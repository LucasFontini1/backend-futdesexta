"""Caixa de notificações privada e registro de inscrições push."""
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Notification, PushSubscription


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'kind', 'title', 'link', 'created_at', 'read_at']
        read_only_fields = fields


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ['endpoint', 'p256dh', 'auth']

    def validate_endpoint(self, value):
        if not value.startswith('https://'):
            raise serializers.ValidationError('Endpoint de push precisa usar HTTPS.')
        return value


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='ler')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=['read_at'])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=['post'], url_path='inscrever-push')
    def subscribe(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        endpoint = serializer.validated_data['endpoint']
        existing = PushSubscription.objects.filter(endpoint=endpoint).first()
        if existing and existing.user_id != request.user.pk:
            raise ValidationError('Inscrição vinculada a outra conta.')
        PushSubscription.objects.update_or_create(
            endpoint=endpoint, defaults={**serializer.validated_data, 'user': request.user}
        )
        return Response({'subscribed': True})
