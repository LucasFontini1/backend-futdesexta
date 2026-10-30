"""Rotas da API do Fut de Sexta."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from core.views.statistics import StatisticsView
from core.views.recurrence import RecurrenceViewSet
from core.views.friendly import FriendlyViewSet
from core.views.competition import CompetitionViewSet, CompetitionInvitationViewSet
from core.views.event import TeamEventViewSet
from core.views.notification import NotificationViewSet
from core.views.calendar import CalendarView
from core.views.location import GeocodeView, MatchWeatherView
from core.views.account_security import VerifyEmailView, PasswordResetRequestView, PasswordResetConfirmView, ChangePasswordView, DeleteAccountView
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
router.register(r'amistosos', FriendlyViewSet, basename='amistosos')
router.register(r'competicoes', CompetitionViewSet, basename='competicoes')
router.register(r'convites-competicao', CompetitionInvitationViewSet, basename='convites-competicao')
router.register(r'eventos', TeamEventViewSet, basename='eventos')
router.register(r'notificacoes', NotificationViewSet, basename='notificacoes')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    path('api/geocodificar/', GeocodeView.as_view(), name='geocode'),
    path('api/partidas/<int:pk>/clima/', MatchWeatherView.as_view(), name='match-weather'),
    path('api/calendario/', CalendarView.as_view(), name='calendar'),
    path('api/estatisticas/', StatisticsView.as_view(), name='statistics'),
    path('api/registro/', UserRegistrationView.as_view(), name='user_registration'),
    path('api/conta/verificar-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('api/conta/recuperar-senha/', PasswordResetRequestView.as_view(), name='recover-password'),
    path('api/conta/redefinir-senha/', PasswordResetConfirmView.as_view(), name='reset-password'),
    path('api/conta/alterar-senha/', ChangePasswordView.as_view(), name='change-password'),
    path('api/conta/excluir/', DeleteAccountView.as_view(), name='delete-account'),
    path('api/', include(router.urls)),
]
