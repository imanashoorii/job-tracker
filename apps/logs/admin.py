from django.contrib import admin

from apps.logs.models import RequestLog
from general.jalali import jalali_datetime


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ("method", "path", "ip_address", "user", "jalali_created_at")
    list_filter = ("method", "created_at")
    search_fields = ("path", "ip_address", "user__username")

    def jalali_created_at(self, obj):
        return jalali_datetime(obj.created_at, time=True)

    jalali_created_at.short_description = "Created (Jalali)"
    jalali_created_at.admin_order_field = "created_at"
