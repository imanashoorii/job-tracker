from rest_framework.routers import DefaultRouter

from apps.jobtracker.views import ApplicationViewSet, BoardViewSet

router = DefaultRouter()
router.register("boards", BoardViewSet, basename="jobtracker-board")
router.register("applications", ApplicationViewSet, basename="jobtracker-application")

urlpatterns = router.urls