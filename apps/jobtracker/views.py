from django.db.models import Count, Q

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.base.mixins import BaseMixin
from apps.base.exceptions import NotAllowed
from apps.logs.mixins import LoggingViewSetMixin
from apps.jobtracker.models import Application, Board
from apps.jobtracker.pagination import ApplicationPagination
from apps.jobtracker.serializers import (
    ApplicationCreateSerializer,
    ApplicationSerializer,
    BoardCreateSerializer,
    BoardRenameSerializer,
    BoardSerializer,
)
from apps.jobtracker.throttling import ApplicationAPIRateThrottle, BoardAPIRateThrottle


class BoardViewSet(BaseMixin, LoggingViewSetMixin, viewsets.ModelViewSet):
    permission_classes_by_action = {
        "list": (IsAuthenticated,),
        "create": (IsAuthenticated,),
        "retrieve": (IsAuthenticated,),
        "partial_update": (IsAuthenticated,),
        "destroy": (IsAuthenticated,),
    }
    serializer_classes_by_action = {
        "list": BoardSerializer,
        "create": BoardCreateSerializer,
        "retrieve": BoardSerializer,
        "partial_update": BoardRenameSerializer,
    }
    throttle_classes_by_action = {
        "list": BoardAPIRateThrottle,
        "create": BoardAPIRateThrottle,
        "retrieve": BoardAPIRateThrottle,
        "partial_update": BoardAPIRateThrottle,
        "destroy": BoardAPIRateThrottle,
    }

    def get_queryset(self):
        return Board.objects.filter(user=self.request.user).annotate(
            applications_count=Count(
                "applications", filter=Q(applications__is_deleted=False)
            )
        )

    def perform_create(self, serializer):
        """Backs the 'new board' modal. Assigns the owner, a default name
        ('Job Tracker N') when the modal's name field was left blank, and
        the next tab order — then logs it the same way LoggingViewSetMixin
        would have, per its own extension contract."""
        name = (serializer.validated_data.get("name") or "").strip()
        if not name:
            count = Board.objects.filter(user=self.request.user).count()
            name = f"Job Tracker {count + 1}"
        order = Board.objects.filter(user=self.request.user).count()
        serializer.save(user=self.request.user, name=name, order=order)
        self._log_on_create(serializer)

    def perform_destroy(self, instance):
        """A user must always keep at least one tab."""
        remaining = Board.objects.filter(user=self.request.user).exclude(pk=instance.pk)
        if not remaining.exists():
            raise NotAllowed("At least one board is required.")
        super().perform_destroy(instance)


class ApplicationViewSet(BaseMixin, LoggingViewSetMixin, viewsets.ModelViewSet):
    pagination_class = ApplicationPagination
    filterset_fields = ("board", "status", "round")

    permission_classes_by_action = {
        "list": (IsAuthenticated,),
        "create": (IsAuthenticated,),
        "retrieve": (IsAuthenticated,),
        "partial_update": (IsAuthenticated,),
        "destroy": (IsAuthenticated,),
    }
    serializer_classes_by_action = {
        "list": ApplicationSerializer,
        "create": ApplicationCreateSerializer,
        "retrieve": ApplicationSerializer,
        "partial_update": ApplicationSerializer,
    }
    throttle_classes_by_action = {
        "list": ApplicationAPIRateThrottle,
        "create": ApplicationAPIRateThrottle,
        "retrieve": ApplicationAPIRateThrottle,
        "partial_update": ApplicationAPIRateThrottle,
        "destroy": ApplicationAPIRateThrottle,
    }

    def get_queryset(self):
        return Application.objects.filter(board__user=self.request.user).select_related(
            "board"
        )

    def perform_create(self, serializer):
        board = serializer.validated_data["board"]
        order = Application.objects.filter(board=board).count()
        serializer.save(order=order)
        self._log_on_create(serializer)
