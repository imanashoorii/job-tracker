from django.contrib.auth import get_user_model

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.authentication.serializers import PasswordLoginSerializer, RegisterSerializer
from apps.authentication.throttling import AuthAPIRateThrottle
from apps.base.mixins import BaseMixin


class PasswordLoginViewSet(BaseMixin, viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()

    serializer_classes_by_action = {
        "login": PasswordLoginSerializer,
        "register": RegisterSerializer,
    }
    permission_classes_by_action = {
        "login": (AllowAny,),
        "register": (AllowAny,),
    }
    throttle_classes_by_action = {
        "login": AuthAPIRateThrottle,
        "register": AuthAPIRateThrottle,
    }

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()
        return Response(data=tokens, status=status.HTTP_201_CREATED)
