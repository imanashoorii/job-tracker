from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from general.enum import UserMessages
from general.utils import get_tokens_for_user
from apps.base.exceptions import InvalidCredentials
from apps.authentication.services import UserServices

User = get_user_model()


class PasswordLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        status, username = UserServices.retrieve_user_by_identifier(username)
        if not status:
            raise InvalidCredentials()

        user = authenticate(username=username, password=password)

        if not user or not api_settings.USER_AUTHENTICATION_RULE(user):
            raise InvalidCredentials()

        access, refresh = get_tokens_for_user(user)
        update_last_login(None, user)
        return {"access": access, "refresh": refresh}


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8, label="Confirm password")

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(UserMessages.USERNAME_TAKEN)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(UserMessages.EMAIL_TAKEN)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": UserMessages.PASSWORDS_DO_NOT_MATCH})
        try:
            validate_password(attrs["password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        return attrs

    def create(self, validated_data):
        access, refresh = UserServices.register_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return {"access": access, "refresh": refresh}