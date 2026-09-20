from typing import Any

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"

    def ready(self: Any) -> None:
        import apps.authentication.signals  # noqa
