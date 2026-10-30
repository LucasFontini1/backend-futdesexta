"""Consulta pública limitada e edição do próprio perfil."""

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.models import User
from core.serializers import UserPrivateSerializer, UserRegistrationSerializer, UserSerializer


class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    throttle_scope = 'users_search'
    queryset = User.objects.filter(is_active=True).order_by('id')

    def get_queryset(self):
        qs = super().get_queryset()
        term = self.request.query_params.get('search', '').strip()
        if self.action == 'list':
            if len(term) < 2:
                return qs.none()
            return qs.filter(Q(name__icontains=term) | Q(username__icontains=term))
        return qs

    @action(
        detail=False, methods=['get', 'patch'], url_path='me', parser_classes=[JSONParser, MultiPartParser, FormParser]
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = UserPrivateSerializer(
                request.user, data=request.data, partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = UserPrivateSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRegistrationView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_scope = 'registration'
