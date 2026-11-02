from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.models import User
from core.serializers import UserSerializer

class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)
    @extend_schema(summary='Dados do usuário autenticado', responses={200: UserSerializer})
    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
