from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from apps.authentication.views import (
    PasswordLoginViewSet,
)

router = DefaultRouter()
router.register("pass", PasswordLoginViewSet, basename="user-password-authentication")

urlpatterns = [
    path("refresh/", TokenRefreshView.as_view(), name="refresh-token"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
]

urlpatterns += router.urls
