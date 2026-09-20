from django.contrib import admin

from apps.jobtracker.models import Application, Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "order", "is_deleted", "created_at")
    list_filter = ("is_deleted",)
    search_fields = ("name", "user__username")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "company", "position", "board", "status", "round",
        "salary", "is_deleted", "updated_at",
    )
    list_filter = ("status", "round", "is_deleted", "board")
    search_fields = ("company", "position")