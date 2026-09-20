from django.db import models

from django.conf import settings
from django.contrib.admin.models import (
    ACTION_FLAG_CHOICES,
    ADDITION,
    CHANGE,
    DELETION,
)
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.base.models import BaseModel
from general.utils import get_client_ip


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_repr = models.CharField(_("object repr"), max_length=200)
    action_flag = models.PositiveSmallIntegerField(
        _("action flag"), choices=ACTION_FLAG_CHOICES
    )
    action_time = models.DateTimeField(
        _("action time"), default=timezone.now, editable=False
    )
    change_message = models.TextField(_("change message"), blank=True, editable=False)

    class Meta:
        verbose_name = _("user activity")
        verbose_name_plural = _("user activities")
        db_table = "user_activity_log"
        ordering = ["-action_time"]

    def __repr__(self):
        text = f"{self.user} - {str(self.action_time)} -> {self.object_repr}"
        return text

    def __str__(self):
        text = f"{self.get_action_flag_msg()} - {self.user}, {str(self.action_time)} -> {self.object_repr}"
        return text

    def is_addition(self):
        return self.action_flag == ADDITION

    def is_change(self):
        return self.action_flag == CHANGE

    def is_deletion(self):
        return self.action_flag == DELETION

    def get_action_flag_msg(self):
        action_message = _("Unknown")

        if self.action_flag == ADDITION:
            action_message = _("Created")
        if self.action_flag == CHANGE:
            action_message = _("Changed")
        if self.action_flag == DELETION:
            action_message = _("Deleted")

        return action_message

    def get_edited_object(self):
        """Return the edited object represented by this log entry."""
        return self.content_type.get_object_for_this_type(pk=self.object_id)


class ErrorLog(BaseModel):
    trace_id = models.CharField(max_length=32)
    data = models.TextField(null=True, blank=True)
    error = models.TextField()
    place = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return f"trace_id: {self.trace_id} - datetime: {self.created_at}"


class RequestLog(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    path = models.TextField()
    data = models.JSONField(null=True, blank=True)
    method = models.CharField(max_length=10)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    @classmethod
    def log(cls, request):
        user = request.user if request.user.is_authenticated else None
        path = request.path
        data = request.data if request.method == "POST" else request.query_params
        method = request.method
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        cls.objects.create(
            user=user,
            path=path,
            data=data,
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
        )
