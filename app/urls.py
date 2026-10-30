"""Rotas da API do Fut de Sexta."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from core.views.statistics import StatisticsView
from core.views.recurrence import RecurrenceViewSet
from core.views import (
    CustomTokenObtainPairView, CustomTokenRefreshView, CustomTokenVerifyView,
    MatchViewSet, TeamInvitationViewSet, TeamViewSet, UserRegistrationView, UserViewSet,
)

router = DefaultRouter()
router.register(r'usuarios', UserViewSet, basename='usuarios')
router.register(r'equipes', TeamViewSet, basename='equipes')
router.register(r'convites-equipe', TeamInvitationViewSet, basename='convites-equipe')
router.register(r'partidas', MatchViewSet, basename='partidas')
router.register(r'recorrencias', RecurrenceViewSet, basename='recorrencias')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    path('api/estatisticas/', StatisticsView.as_view(), name='statistics'),
    path('api/registro/', UserRegistrationView.as_view(), name='user_registration'),
    path('api/', include(router.urls)),
]
