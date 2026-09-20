from typing import Union

from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login

from general.enum import UserMessages
from general.utils import get_tokens_for_user
from general.validations import validate_email

User = get_user_model()


class UserServices:

    @staticmethod
    def __generate_tokens(user: User) -> tuple[str, str]:
        return get_tokens_for_user(user)

    @staticmethod
    def retrieve_user_by_identifier(identifier: str) -> tuple[bool, Union[str, User]]:
        """
        Retrieve a user's username by identifier (email or username).
        """
        if validate_email(identifier):
            user = User.objects.filter(email=identifier).first()
        else:
            user = User.objects.filter(username=identifier).first()

        if not user:
            return False, UserMessages.INVALID_CREDENTIALS

        return True, user.username

    @classmethod
    def register_user(cls, username: str, email: str, password: str) -> tuple[str, str]:
        """
        Creates a new user and returns a fresh access/refresh token pair,
        the same shape PasswordLoginSerializer returns on login.
        """
        user = User.objects.create_user(username=username, email=email, password=password)
        access, refresh = cls.__generate_tokens(user)
        update_last_login(None, user)
        return access, refresh